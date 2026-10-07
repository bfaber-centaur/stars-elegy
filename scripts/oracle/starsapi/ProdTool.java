import java.io.*;
import java.util.*;
import org.starsautohost.starsapi.block.*;
import org.starsautohost.starsapi.encryption.Decryptor;

// Decode or edit planet and production-queue state in Stars! game files with
// the StarsAPI codec (built by scripts/oracle/hst-edit at a pinned commit).
// Used to set up oracle experiments (docs/ORACLE.md, "Setting up a state").
//   dump FILE...                         planet/queue/player/event state
//   edit IN OUT key=value...             edit planet P (default 7) and player 0
// keys: planet=N fe= bo= ge= pop= excess= mines= factories= defenses=
//       leftover=0|1 researchPct=N queue=SPEC (SPEC: id:count:pct:kind,... ; kind 1=planetary item, 2=design; "none" removes)
public class ProdTool {
  static long le32(byte[] d, int o) { return (d[o]&0xffL)|(d[o+1]&0xffL)<<8|(d[o+2]&0xffL)<<16|((long)d[o+3])<<24; }
  static String hex(byte[] d, int n) { StringBuilder sb=new StringBuilder(); for(int i=0;i<n;i++) sb.append(String.format("%02x",d[i]&0xff)); return sb.toString(); }

  public static void main(String[] a) throws Exception {
    if (a[0].equals("dump")) { for (int i=1;i<a.length;i++) dump(a[i]); }
    else if (a[0].equals("edit")) edit(a);
    else if (a[0].equals("roundtrip")) { List<Block> bl=new Decryptor().readFile(a[1]); for (Block b: bl) if (b instanceof PartialPlanetBlock) b.encode(); new Decryptor().writeBlocks(a[2], bl, false); }
  }

  static void dump(String f) throws Exception {
    String n = f.replaceAll(".*/", "");
    int turn=-1;
    for (Block b : new Decryptor().readFile(f)) {
      if (b instanceof FileHeaderBlock) { turn=((FileHeaderBlock)b).turn; System.out.printf("%s header turn=%d year=%d%n", n, turn, 2400+turn); }
      else if (b instanceof PartialPlanetBlock) {
        PartialPlanetBlock q=(PartialPlanetBlock)b; if (q.owner<0) continue;
        int def12 = (q.defenses & 0xff) | ((q.unknownInstallationsByte & 0x0f) << 8);
        int scan = ((q.unknownInstallationsByte & 0xf0) >> 4) | (q.hasScanner?0:16);
        System.out.printf("%s planet=%d owner=%d fe=%d bo=%d ge=%d pop=%d excess=%d mines=%d factories=%d defenses=%d leftover=%b scannerField=%d conc=%d/%d/%d hab=%d/%d/%d%n",
          n, q.planetNumber, q.owner, q.ironium, q.boranium, q.germanium, q.population, q.excessPop, q.mines, q.factories, def12,
          q.contributeOnlyLeftoverResourcesToResearch, scan, q.ironiumConc, q.boraniumConc, q.germaniumConc, q.gravity, q.temperature, q.radiation);
      }
      else if (b instanceof ProductionQueueBlock) {
        byte[] d=b.getDecryptedData(); StringBuilder sb=new StringBuilder();
        for (int i=0;i+4<=b.size;i+=4) { int w0=(d[i]&0xff)|(d[i+1]&0xff)<<8, w1=(d[i+2]&0xff)|(d[i+3]&0xff)<<8;
          sb.append(String.format(" [id=%d count=%d pct=%d kind=%d hi=%d]", (w0>>10)|((w1&1)<<6), w0&0x3ff, (w1>>4)&0x7f, (w1>>1)&7, w1>>11)); }
        System.out.printf("%s queue n=%d%s%n", n, b.size/4, sb);
      }
      else if (b instanceof PlayerBlock) {
        PlayerBlock p=(PlayerBlock)b; if (p.fullDataBytes==null) continue; byte[] d=p.fullDataBytes; int B=8;
        StringBuilder lv=new StringBuilder(), acc=new StringBuilder();
        for (int i=0;i<6;i++){ lv.append(i==0?"":",").append(d[0x1a-B+i]); acc.append(i==0?"":",").append(le32(d,0x20-B+4*i)); }
        System.out.printf("%s player=%d researchPct=%d field=%d resRes=%d levels=%s accum=%s%n", n, p.playerNumber, d[0x38-B], d[0x39-B]&15, le32(d,0x3a-B), lv, acc);
      }
      else if (b.typeId == 12) { System.out.printf("%s events %s%n", n, hex(b.getDecryptedData(), b.size)); }
    }
  }

  static void edit(String[] a) throws Exception {
    Map<String,String> kv=new LinkedHashMap<>();
    for (int i=3;i<a.length;i++){ String[] s=a[i].split("=",2); kv.put(s[0],s[1]); }
    int planet = Integer.parseInt(kv.getOrDefault("planet","7"));
    List<Block> bl = new Decryptor().readFile(a[1]);
    List<Block> out = new ArrayList<>();
    boolean found=false;
    for (int i=0;i<bl.size();i++) {
      Block b=bl.get(i);
      if (b instanceof ProductionQueueBlock && found && kv.containsKey("queue") && out.get(out.size()-1) instanceof PartialPlanetBlock && ((PartialPlanetBlock)out.get(out.size()-1)).planetNumber==planet) continue; // drop old
      if (b instanceof PlayerBlock && kv.containsKey("researchPct")) {
        PlayerBlock p=(PlayerBlock)b; if (p.fullDataBytes!=null && p.playerNumber==0) { p.fullDataBytes[0x38-8]=(byte)Integer.parseInt(kv.get("researchPct")); p.encode(); }
      }
      out.add(b);
      if (b instanceof PartialPlanetBlock && ((PartialPlanetBlock)b).planetNumber==planet && ((PartialPlanetBlock)b).owner>=0) {
        found=true;
        PartialPlanetBlock q=(PartialPlanetBlock)b;
        for (Map.Entry<String,String> e: kv.entrySet()) {
          String k=e.getKey(); String v=e.getValue();
          switch (k) {
            case "fe": q.ironium=Long.parseLong(v); break;
            case "bo": q.boranium=Long.parseLong(v); break;
            case "ge": q.germanium=Long.parseLong(v); break;
            case "pop": q.population=Long.parseLong(v); break;
            case "excess": q.excessPop=Integer.parseInt(v); break;
            case "mines": q.mines=Integer.parseInt(v); break;
            case "factories": q.factories=Integer.parseInt(v); break;
            case "defenses": { int d=Integer.parseInt(v); q.defenses=d&0xff; q.unknownInstallationsByte=(byte)((q.unknownInstallationsByte&0xf0)|((d>>8)&0x0f)); break; }
            case "leftover": q.contributeOnlyLeftoverResourcesToResearch=v.equals("1"); break;
          }
        }
        q.encode();
        if (kv.containsKey("queue") && !kv.get("queue").equals("none")) {
          String[] items=kv.get("queue").split(",");
          byte[] d=new byte[items.length*4];
          for (int j=0;j<items.length;j++){ String[] f=items[j].split(":");
            int id=Integer.parseInt(f[0]), cnt=Integer.parseInt(f[1]), pct=Integer.parseInt(f[2]), kind=Integer.parseInt(f[3]);
            int w0=((id&0x3f)<<10)|(cnt&0x3ff), w1=((pct&0x7f)<<4)|((kind&7)<<1)|((id>>6)&1);
            d[4*j]=(byte)w0; d[4*j+1]=(byte)(w0>>8); d[4*j+2]=(byte)w1; d[4*j+3]=(byte)(w1>>8); }
          ProductionQueueBlock pq=new ProductionQueueBlock();
          pq.setDecryptedData(d, d.length); pq.setData(d.clone(), d.length);
          out.add(pq);
        }
      }
    }
    if (!found) throw new Exception("planet not found");
    new Decryptor().writeBlocks(a[2], out, false);
  }
}
