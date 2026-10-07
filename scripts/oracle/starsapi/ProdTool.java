import java.io.*;
import java.util.*;
import org.starsautohost.starsapi.block.*;
import org.starsautohost.starsapi.encryption.Decryptor;

// Decode or edit planet and production-queue state in Stars! game files with
// the StarsAPI codec (built by scripts/oracle/hst-edit at a pinned commit).
// Used to set up oracle experiments (docs/ORACLE.md, "Setting up a state").
//   dump FILE...                         planet/queue/player/event state
//   edit IN OUT key=value...             edit planet P (default 7) and player 0
//   xy IN.XY OUT.XY OFF:HEX...            set game-record bytes (options, victory conditions)
// keys: planet=N fe= bo= ge= pop= excess= mines= factories= defenses=
//       leftover=0|1 researchPct=N queue=SPEC (SPEC: id:count:pct:kind,... ; kind 1=planetary item, 2=design; "none" removes)
//       starbase=0|1 (planet's has-starbase flag; 1 keeps the existing design slot)
//       race edits on player 0: prt=N lrt=HEX (32-bit LRT word) stat=I:V[/I:V...] (race stat I = byte 0x36+I of the full data)
//       hab=C,C,C,L,L,L,H,H,H (race hab centre/low/high per axis grav,temp,rad; full data bytes 8..16)
//       env=G,T,R (planet's current environment, clicks) orig=G,T,R (original environment; marks the planet terraformed)
//       tech=E,W,P,C,EL,B (current tech levels; full data bytes 0x12..0x17)
//       mt=HEX (Mystery Trader items owned, 16-bit mask; full data bytes 0x4a..0x4b, little-endian)
//       field=CUR,NEXT (research field byte, full data byte 0x31: low nibble current field 0-5,
//       high nibble next-field choice 0-5, 6 same field, 7 lowest field)
//       conc=I,B,G (planet's mineral concentrations; fraction bytes kept)
public class ProdTool {
  static long le32(byte[] d, int o) { return (d[o]&0xffL)|(d[o+1]&0xffL)<<8|(d[o+2]&0xffL)<<16|((long)d[o+3])<<24; }
  static String hex(byte[] d, int n) { StringBuilder sb=new StringBuilder(); for(int i=0;i<n;i++) sb.append(String.format("%02x",d[i]&0xff)); return sb.toString(); }

  public static void main(String[] a) throws Exception {
    if (a[0].equals("dump")) { for (int i=1;i<a.length;i++) dump(a[i]); }
    else if (a[0].equals("edit")) edit(a);
    else if (a[0].equals("xy")) xy(a);
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
        // An omitted installations block means the game defaults: no
        // scanner (31). StarsAPI leaves its fields zeroed, which read as 16.
        int scan = !q.hasInstallations ? 31 : ((q.unknownInstallationsByte & 0xf0) >> 4) | (q.hasScanner?0:16);
        System.out.printf("%s planet=%d owner=%d fe=%d bo=%d ge=%d pop=%d excess=%d mines=%d factories=%d defenses=%d leftover=%b scannerField=%d conc=%d/%d/%d frac=%s hab=%d/%d/%d%s starbase=%s%n",
          n, q.planetNumber, q.owner, q.ironium, q.boranium, q.germanium, q.population, q.excessPop, q.mines, q.factories, def12,
          q.contributeOnlyLeftoverResourcesToResearch, scan, q.ironiumConc, q.boraniumConc, q.germaniumConc, hex(q.fractionalMinConcBytes, q.fractionalMinConcBytes.length), q.gravity, q.temperature, q.radiation,
          q.isTerraformed ? String.format(" orig=%d/%d/%d", q.origGravity, q.origTemperature, q.origRadiation) : "", q.hasStarbase ? Integer.toString(q.starbaseDesign) : "none");
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
        System.out.printf("%s player=%d researchPct=%d field=%d next=%d resRes=%d levels=%s accum=%s%n", n, p.playerNumber, d[0x38-B], d[0x39-B]&15, (d[0x39-B]>>4)&15, le32(d,0x3a-B), lv, acc);
        StringBuilder st=new StringBuilder(); for (int i=0;i<14;i++) st.append(i==0?"":",").append(d[0x36+i]&0xff);
        System.out.printf("%s race player=%d prt=%d lrt=%08x stats=%s growth=%d hab=%d,%d,%d/%d,%d,%d/%d,%d,%d%n", n, p.playerNumber, d[0x44]&0xff, le32(d,0x46)&0xffffffffL, st, d[0x11], d[8],d[9],d[10],d[11],d[12],d[13],d[14],d[15],d[16]);
      }
      else if (b.typeId == 7) { System.out.printf("%s game %s%n", n, hex(b.getDecryptedData(), Math.min(32, b.size))); }
      else if (b.typeId == 45) { System.out.printf("%s scores %s%n", n, hex(b.getDecryptedData(), b.size)); }
      else if (b.typeId == 12) { System.out.printf("%s events %s%n", n, hex(b.getDecryptedData(), b.size)); }
    }
  }

  // xy IN.XY OUT.XY OFF:HEX...: set bytes of the game record (.XY planets block
  // data; OFF hex). 0x10 game options (bit 1 slower tech), 0x14+I victory condition I
  // (bit 7 enabled, low 7 bits the value).
  static void xy(String[] a) throws Exception {
    List<Block> bl = new Decryptor().readFile(a[1]);
    for (Block b: bl) if (b.typeId == 7) { byte[] d=b.getDecryptedData();
      for (int i=3;i<a.length;i++){ String[] f=a[i].split(":"); d[Integer.parseInt(f[0],16)]=(byte)Integer.parseInt(f[1],16); }
      b.setDecryptedData(d, b.size); }
    new Decryptor().writeBlocks(a[2], bl, false);
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
      if (b instanceof PlayerBlock && ((PlayerBlock)b).fullDataBytes!=null && ((PlayerBlock)b).playerNumber==0) {
        PlayerBlock p=(PlayerBlock)b; byte[] d=p.fullDataBytes; boolean ch=false;
        if (kv.containsKey("researchPct")) { d[0x38-8]=(byte)Integer.parseInt(kv.get("researchPct")); ch=true; }
        if (kv.containsKey("prt")) { d[0x44]=(byte)Integer.parseInt(kv.get("prt")); ch=true; }
        if (kv.containsKey("lrt")) { long v=Long.parseLong(kv.get("lrt"),16); for (int k=0;k<4;k++) d[0x46+k]=(byte)(v>>(8*k)); ch=true; }
        if (kv.containsKey("stat")) { for (String sv: kv.get("stat").split("/")) { String[] f=sv.split(":"); d[0x36+Integer.parseInt(f[0])]=(byte)Integer.parseInt(f[1]); } ch=true; }
        if (kv.containsKey("tech")) { String[] t=kv.get("tech").split(","); for (int k=0;k<6;k++) d[0x1a-8+k]=(byte)Integer.parseInt(t[k]); ch=true; }
        if (kv.containsKey("field")) { String[] f=kv.get("field").split(","); d[0x39-8]=(byte)((Integer.parseInt(f[1])<<4)|Integer.parseInt(f[0])); ch=true; }
        if (kv.containsKey("mt")) { int v=Integer.parseInt(kv.get("mt"),16); d[0x4a]=(byte)v; d[0x4b]=(byte)(v>>8); ch=true; }
        if (kv.containsKey("hab")) { String[] h=kv.get("hab").split(","); for (int k=0;k<9;k++) d[8+k]=(byte)Integer.parseInt(h[k]); ch=true; }
        if (ch) p.encode();
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
            case "starbase": q.hasStarbase=v.equals("1"); break;
            case "env": { String[] g=v.split(","); q.gravity=Integer.parseInt(g[0]); q.temperature=Integer.parseInt(g[1]); q.radiation=Integer.parseInt(g[2]); break; }
            case "conc": { String[] g=v.split(","); q.ironiumConc=Integer.parseInt(g[0]); q.boraniumConc=Integer.parseInt(g[1]); q.germaniumConc=Integer.parseInt(g[2]); break; }
            case "orig": { String[] g=v.split(","); if (!q.isTerraformed) { q.isTerraformed=true; }
              q.origGravity=Integer.parseInt(g[0]); q.origTemperature=Integer.parseInt(g[1]); q.origRadiation=Integer.parseInt(g[2]); break; }
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
