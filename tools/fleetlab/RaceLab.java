// RaceLab: read and edit Stars! race files (.R1 ... .R16) for oracle new games.
//
//   racelab dump FILE...                race fields, checksum and advantage points
//   racelab edit IN OUT KEY=V...        copy IN to OUT with fields changed and the
//                                       footer checksum recomputed
//
// KEYs (offsets are into the race block after its 8-byte header, the same
// layout as a host file's player block):
//   prt=N        primary trait (0 HE, 1 SS, 2 WM, 3 CA, 4 IS, 5 SD, 6 PP, 7 IT,
//                8 AR, 9 JOAT)                           byte 0x44
//   lrt=MASK     lesser traits, bit i = LRT i (0 IFE, 1 TT, 2 ARM, 3 ISB, 4 GR,
//                5 UR, 6 MA, 7 NRSE, 8 CE, 9 OBRM, 10 NAS, 11 LSP, 12 BET, 13 RS)
//                                                        word 0x46
//   spend=N      leftover points (race stat 7): 0 surface minerals,
//                1 mineral concentrations, 2 mines, 3 factories, 4 defenses
//                                                        byte 0x3d
//   growth=N     maximum growth rate in percent          byte 0x11
//   name=S plural=S
//
// Advantage points come from StarsAPI's racebuilder (craigstars port). It
// covers PRT, LRTs, growth, habitability, economy and research costs as
// stored here; a negative value is an illegal race. Check a crafted race in
// the game (message 0x117) before relying on the figure.
import java.util.*;
import org.starsautohost.starsapi.Util;
import org.starsautohost.starsapi.block.*;
import org.starsautohost.starsapi.encryption.Decryptor;
import org.starsautohost.racebuilder.craigstars.*;

public class RaceLab {
    static final String[] PRTS = {"HE", "SS", "WM", "CA", "IS", "SD", "PP", "IT", "AR", "JOAT"};

    public static void main(String[] a) throws Exception {
        if (a.length >= 2 && a[0].equals("dump")) {
            for (int i = 1; i < a.length; i++) dump(a[i]);
        } else if (a.length >= 3 && a[0].equals("edit")) {
            edit(a[1], a[2], Arrays.copyOfRange(a, 3, a.length));
        } else {
            System.err.println("usage: racelab dump FILE... | racelab edit IN OUT KEY=V...");
            System.exit(2);
        }
    }

    static List<Block> read(String f) throws Exception {
        List<Block> bl = new Decryptor().readFile(f);
        if (bl.size() != 3 || !(bl.get(1) instanceof PlayerBlock) || !(bl.get(2) instanceof FileFooterBlock))
            throw new Exception(f + ": not a race file (header, player block, footer)");
        return bl;
    }

    static void dump(String f) throws Exception {
        List<Block> bl = read(f);
        PlayerBlock p = (PlayerBlock) bl.get(1);
        byte[] d = p.fullDataBytes;
        int sum = Util.checkSumRaceFile(p.raceFileStructData);
        int lrt = Util.read16(d, 0x46) & 0x3fff;
        StringBuilder st = new StringBuilder();
        for (int i = 0; i < 16; i++) st.append(i == 0 ? "" : ",").append(d[0x36 + i] & 0xff);
        System.out.printf("%s name=%s/%s prt=%s lrt=%#x growth=%d hab=%d,%d,%d/%d,%d,%d/%d,%d,%d stats=%s checksum=%s points=%d%n",
            f, p.nameSingular, p.namePlural, PRTS[d[0x44]], lrt, d[0x11],
            d[8] & 0xff, d[9] & 0xff, d[10] & 0xff, d[11] & 0xff, d[12] & 0xff, d[13] & 0xff,
            d[14] & 0xff, d[15] & 0xff, d[16] & 0xff, st,
            sum == ((FileFooterBlock) bl.get(2)).checksum ? "ok" : "BAD", points(d));
    }

    static int points(byte[] d) {
        Race r = Race.getHumanoid();
        r.setPRT(PRT.values()[d[0x44]]);
        Set<LRT> s = new HashSet<>();
        int lrt = Util.read16(d, 0x46);
        for (LRT l : LRT.values()) if ((lrt >> l.ordinal() & 1) != 0) s.add(l);
        r.setLRTs(s);
        r.setGrowthRate(d[0x11] / 100f);
        int[] c = {d[8] & 0xff, d[9] & 0xff, d[10] & 0xff}, lo = {d[11] & 0xff, d[12] & 0xff, d[13] & 0xff},
              hi = {d[14] & 0xff, d[15] & 0xff, d[16] & 0xff};
        boolean[] imm = {c[0] == 255, c[1] == 255, c[2] == 255};
        r.setImmuneGrav(imm[0]); r.setImmuneTemp(imm[1]); r.setImmuneRad(imm[2]);
        r.setHabLow(new Hab(imm[0] ? 15 : lo[0], imm[1] ? 15 : lo[1], imm[2] ? 15 : lo[2]));
        r.setHabHigh(new Hab(imm[0] ? 85 : hi[0], imm[1] ? 85 : hi[1], imm[2] ? 85 : hi[2]));
        r.setColonistsPerResource(100 * (d[0x36] & 0xff));
        r.setFactoryOutput(d[0x37]); r.setFactoryCost(d[0x38]); r.setNumFactories(d[0x39]);
        r.setMineOutput(d[0x3a]); r.setMineCost(d[0x3b]); r.setNumMines(d[0x3c]);
        ResearchCostLevel[] lv = new ResearchCostLevel[6];
        for (int f = 0; f < 6; f++) lv[f] = d[0x3e + f] == 0 ? ResearchCostLevel.Extra : d[0x3e + f] == 2 ? ResearchCostLevel.Less : ResearchCostLevel.Standard;
        r.setResearchCost(new ResearchCost(lv[0], lv[1], lv[2], lv[3], lv[4], lv[5]));
        return RacePointsCalculator.getAdvantagePoints(r);
    }

    static void edit(String in, String out, String[] kv) throws Exception {
        List<Block> bl = read(in);
        PlayerBlock p = (PlayerBlock) bl.get(1);
        byte[] d = p.fullDataBytes;
        for (String s : kv) {
            String k = s.substring(0, s.indexOf('=')), v = s.substring(s.indexOf('=') + 1);
            switch (k) {
                case "prt": d[0x44] = (byte) Integer.parseInt(v); break;
                case "lrt": Util.write16(d, 0x46, (Util.read16(d, 0x46) & ~0x3fff) | (Integer.decode(v) & 0x3fff)); break;
                case "spend": d[0x3d] = (byte) Integer.parseInt(v); break;
                case "growth": d[0x11] = (byte) Integer.parseInt(v); break;
                case "name": p.nameSingular = v; break;
                case "plural": p.namePlural = v; break;
                default: throw new Exception("unknown key " + k);
            }
        }
        p.encode();
        p.decode();
        FileFooterBlock foot = new FileFooterBlock();
        foot.checksum = Util.checkSumRaceFile(p.raceFileStructData);
        foot.encode();
        new Decryptor().writeBlocks(out, Arrays.asList(bl.get(0), p, foot), false);
        System.out.println("wrote " + out);
        dump(out);
    }
}
