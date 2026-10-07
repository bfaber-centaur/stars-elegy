import java.nio.file.*;
import java.util.*;

import org.starsautohost.starsapi.Util;
import org.starsautohost.starsapi.block.*;
import org.starsautohost.starsapi.encryption.Decryptor;
import org.starsautohost.starsapi.items.Items;

// CombatLab: build controlled multi-player battle starts by editing a Stars!
// .HST with StarsAPI, and dump designs, fleets, battle plans and battle
// records from .HST/.M files.
//
//   CombatLab dump FILE...
//   CombatLab build BASE.HST SPEC OUT.HST
//
// SPEC is line based ('#' starts a comment). Players are numbered from 0.
//   tech P FIELD LEVEL              set a tech level (energy weapons prop con elec bio)
//   lrt P MASK                      set the lesser racial traits bit mask (StarsAPI order)
//   prt P N                         set the primary racial trait (0 HE 1 SS 2 WM 3 CA 4 IS
//                                   5 SD 6 PP 7 IT 8 AR 9 JOAT)
//   hab P C,C,C,L,L,L,H,H,H         set the habitability centre, low and high per axis
//                                   (gravity, temperature, radiation)
//   research P PCT                  set the share of resources spent on research
//   field P FIELD                   set the current research field
//   defqueue P ID:COUNT[,...]|none  set P's default production queue for new colonies (at
//                                   most 12 items; ID = planetary item id, 0 auto mines,
//                                   1 auto factories, 2 auto defenses, 3 auto alchemy,
//                                   4 auto min terraform, 5 auto max terraform, 6 auto packets)
//   defleftover P 0|1               set P's default "only leftover to research" for new colonies
//   mt P HEX                        set the Mystery Trader items P owns (16-bit mask, one bit
//                                   per item; 0 = none). Designs may use Mystery Trader parts
//                                   by name whatever the mask (see docs/ORACLE.md)
//   queue N ID:COUNT[:PCT]:KIND[,...]|none
//                                   replace planet N's production queue (owned planets).
//                                   KIND 2 = ship design ID of the planet's owner, KIND 1 =
//                                   planetary item ID (as defqueue); COUNT up to 1023; PCT
//                                   = percent of the first unit already done (default 0)
//   relation P Q REL                P's relation to Q: 0 neutral, 1 friend, 2 enemy
//   design P N HULL, SLOT, ... = NAME
//                                   ship design N of player P. HULL and SLOTs are
//                                   StarsAPI names or abbreviations, one SLOT per hull
//                                   slot in hull order: "COUNT ITEM", "ITEM" (fills the
//                                   slot) or "empty". Any design line for P replaces
//                                   all of P's ship designs.
//   sbdesign P N HULL, SLOT, ... = NAME
//                                   the same for starbase designs
//   plan P K TACTIC PRIMARY SECONDARY WHO [dump] = NAME
//                                   battle plan K of player P; numbers as in
//                                   StarsAPI BattlePlanBlock (tactic 0-5, targets 0-7,
//                                   who 0 nobody 1 enemies 2 neutral+enemies 3 everyone
//                                   4+i player i)
//   fleet P ID [planet N] at X Y ships D:C[,D:C...] [plan K] [fuel F] [cargo IR BO GE COL]
//         [dmg D:UNITS:PCT[,...]]  (damage word per design: UNITS/500 of armor on PCT% of ships)
//                                   a stationary fleet (one waypoint, at its position),
//                                   orbiting planet N if given (X Y must be its position)
//         [target fleet OWNER ID] [task TASK] [to X Y [planet N|thing ID|fleet OWNER ID] warp W [task TASK]]...
//                                   waypoint tasks (takeover corpus): "task" sets the task
//                                   of the waypoint before it (waypoint 0 when first), "to"
//                                   adds a waypoint. TASK: colonize | scrap | mine |
//                                   unload (all colonists) | merge (into the waypoint's
//                                   fleet) | transfer K (give the fleet to the K-th other
//                                   player) | lay [YEARS] (lay mines; YEARS
//                                   word, default 5 = indefinitely) | transport A:V,A:V,A:V,A:V,A:V
//                                   (Ir, Bo, Ge, colonists, fuel; action 0-9, value in
//                                   kT or 100s of colonists; "-" for no order). "target
//                                   fleet" makes waypoint 0 target a fleet (id number |
//                                   owner << 9, type 0x12) for merge and fleet transport
//   planetset N KEY=V...            planet N's fields after any "planet" line: mines=
//                                   factories= defenses= excess= fe= bo= ge= (installed/
//                                   surface values; owned planets) scanner=ID (planetary
//                                   scanner id, 31 = none) conc=I,B,G env=G,T,R
//                                   orig=G,T,R (original environment; sets "terraformed")
//                                   sbdmg=U (starbase damage, U/500 of its armor)
//                                   driver=DEST[,WARP] (mass-driver packet destination
//                                   planet and chosen packet warp; needs a starbase)
//   thing minefield OWNER NUM X Y COUNT [kind std|heavy|bump] [det] [known MASK] [seen MASK]
//   thing packet OWNER NUM X Y DEST WARP IR BO GE [class K] [moved] [bit15]
//   thing wormhole NUM X Y PARTNER CLASS [years N] [seen MASK] [seen2 MASK]
//   thing trader NUM X Y DX DY WARP [met MASK] [item I]
//   thing raw HEX                   (18 bytes)
//                                   universe objects (objects corpus), written as the
//                                   host file's object blocks: a count block, then one
//                                   18-byte record per object sorted by id (type << 13 |
//                                   owner << 9 | number), before the battle plans. Replaces
//                                   every object already in BASE. Layout: docs/ORACLE.md
//                                   "Universe objects". PARTNER is the other wormhole's
//                                   NUM; DEST a planet number; MASKs are player bit masks.
//   planet N [owner P] [pop X] [starbase D|none] [scanner none|on]
//                                   make planet N player P's (installations copied from
//                                   P's homeworld, none built), set its population (in
//                                   the file's units) and its starbase design (starbase
//                                   bytes copied from P's homeworld starbase); "scanner
//                                   none" removes the planetary scanner (scanner id 31)
// Every fleet in BASE is replaced by the SPEC fleets.
public class CombatLab {
    static final String[] TECH = {"energy", "weapons", "prop", "con", "elec", "bio"};

    public static void main(String[] args) throws Exception {
        if (args.length >= 2 && args[0].equals("dump")) {
            for (int i = 1; i < args.length; i++) dump(args[i]);
        } else if (args.length == 4 && args[0].equals("build")) {
            build(args[1], args[2], args[3]);
        } else {
            System.err.println("usage: CombatLab dump FILE... | build BASE.HST SPEC OUT.HST");
            System.exit(2);
        }
    }

    // ------------------------------------------------------------------ dump

    static String itemName(int category, int id) {
        int key = (category << 8) | id;
        for (Map.Entry<String, Integer> e : Items.itemsByName.entrySet())
            if (e.getValue() == key) return e.getKey();
        return String.format("%x:%d", category, id);
    }

    static String hullName(int hull) {
        for (Map.Entry<String, Integer> e : Items.hullsByName.entrySet())
            if (e.getValue() == hull) return e.getKey();
        return "hull" + hull;
    }

    static String designString(DesignBlock d) {
        StringBuilder sb = new StringBuilder(hullName(d.hullId));
        if (d.isFullDesign)
            for (DesignBlock.Slot s : d.slots)
                sb.append(", ").append(s.count == 0 ? "empty" : s.count + " " + itemName(s.category, s.itemId));
        return sb.toString();
    }

    static void dump(String f) throws Exception {
        List<Block> blocks = new Decryptor().readFile(f);
        boolean host = f.toUpperCase().endsWith(".HST");
        List<PlayerBlock> players = new ArrayList<>();
        int shipSeen = 0, sbSeen = 0, filePlayer = -1, lastPlanet = -1;
        StringBuilder battle = null;
        int turn = -1;
        for (Block b : blocks) {
            if (battle != null && b.typeId != BlockType.BATTLE_CONTINUATION) {
                printBattle(f, turn, battle.toString());
                battle = null;
            }
            if (b instanceof FileHeaderBlock) {
                FileHeaderBlock h = (FileHeaderBlock) b;
                turn = h.turn;
                filePlayer = h.playerNumber;
                System.out.printf("%s file turn=%d year=%d player=%d%n", f, h.turn, 2400 + h.turn, h.playerNumber);
            } else if (b instanceof PlayerBlock) {
                PlayerBlock p = (PlayerBlock) b;
                players.add(p);
                StringBuilder sb = new StringBuilder();
                if (p.fullDataBytes != null) {
                    for (int i = 0; i < 6; i++) sb.append(' ').append(TECH[i]).append('=').append(p.fullDataBytes[0x12 + i]);
                    sb.append(String.format(" prt=%d lrt=%04x", p.fullDataBytes[0x44],
                        ((p.fullDataBytes[0x47] & 0xff) << 8) | (p.fullDataBytes[0x46] & 0xff)));
                    sb.append(String.format(" mt=%04x", Util.read16(p.fullDataBytes, 0x4a)));
                    sb.append(" accum=");
                    for (int i = 0; i < 6; i++)
                        sb.append(i == 0 ? "" : ",").append(Util.read32(p.fullDataBytes, 0x18 + 4 * i));
                    sb.append(String.format(" researchPct=%d field=%d", p.fullDataBytes[0x30], p.fullDataBytes[0x31] & 15));
                    sb.append(" hab=");
                    for (int i = 0; i < 9; i++) sb.append(i == 0 ? "" : ",").append(p.fullDataBytes[8 + i] & 0xff);
                    // advantage points (RaceLab, StarsAPI racebuilder): negative = a race the
                    // host degrades at the start of the year (message 0x117)
                    try { sb.append(" points=").append(RaceLab.points(p.fullDataBytes)); } catch (Exception e) { sb.append(" points=?"); }
                    // default production queue for new colonies (count at 0x4f, words id | count << 6 from 0x50)
                    // and the default "only leftover to research" bit (0x4e bit 0)
                    sb.append(" defqueue=");
                    int nq = p.fullDataBytes[0x4f] & 0xff;
                    for (int i = 0; i < nq && 0x51 + 2 * i < p.fullDataBytes.length; i++) {
                        int w = Util.read16(p.fullDataBytes, 0x50 + 2 * i);
                        sb.append(i == 0 ? "" : ",").append(w & 0x3f).append(':').append(w >> 6);
                    }
                    if (nq == 0) sb.append("none");
                    sb.append(" defleftover=").append(p.fullDataBytes[0x4e] & 1);
                    // Mystery Trader parts owned (bytes 0x4a, 0x4b as StarsAPI's setMtMask writes them)
                    sb.append(String.format(" mt=%02x%02x", p.fullDataBytes[0x4a] & 0xff, p.fullDataBytes[0x4b] & 0xff));
                }
                System.out.printf("%s player %d shipdesigns=%d sbdesigns=%d fleets=%d relations=%s%s%n", f,
                    p.playerNumber, p.shipDesignCount, p.starbaseDesignCount, p.fleets,
                    Arrays.toString(p.playerRelations), sb);
            } else if (b instanceof DesignBlock) {
                DesignBlock d = (DesignBlock) b;
                String owner = "?";
                if (host) {
                    // HST: all ship designs (player order), then later all starbase designs.
                    int seen = d.isStarbase ? sbSeen++ : shipSeen++;
                    for (PlayerBlock p : players) {
                        int n = d.isStarbase ? p.starbaseDesignCount : p.shipDesignCount;
                        if (seen < n) { owner = "" + p.playerNumber; break; }
                        seen -= n;
                    }
                } else if (d.isFullDesign) owner = "" + filePlayer;
                System.out.printf("%s %s owner=%s n=%d mass=%d armor=%d full=%s :: %s%n", f,
                    d.isStarbase ? "sbdesign" : "design", owner, d.designNumber, d.mass,
                    d.isFullDesign ? d.armor : -1, d.isFullDesign, designString(d));
            } else if (b instanceof PartialFleetBlock) {
                PartialFleetBlock fl = (PartialFleetBlock) b;
                StringBuilder ships = new StringBuilder();
                for (int i = 0; i < 16; i++) if (fl.shipCount[i] > 0)
                    ships.append(ships.length() > 0 ? "," : "").append(i).append(':').append(fl.shipCount[i]);
                StringBuilder dmg = new StringBuilder();
                if (fl.kindByte == PartialFleetBlock.FULL_KIND)
                    for (int i = 0; i < 16; i++) if ((fl.damagedShipTypes & (1 << i)) != 0)
                        dmg.append(String.format(" dmg%d=%d/%d%%", i, fl.damagedShipInfo[i] >> 7, fl.damagedShipInfo[i] & 0x7f));
                if (fl.kindByte != PartialFleetBlock.FULL_KIND)   // another player's fleet: heading, warp, mass;
                    // each heading byte stores the component + 127 (SC-027); a fleet that did not move has 0/0
                    dmg.append(String.format(" dx=%d dy=%d warp=%d wbits=%02x mass=%d",
                        (fl.deltaX & 0xff) - 127, (fl.deltaY & 0xff) - 127, fl.warp, fl.unknownBitsWithWarp, fl.mass));
                System.out.printf("%s fleet owner=%d id=%d kind=%d x=%d y=%d obj=%d ships=%s cargo=%d/%d/%d/%d fuel=%d plan=%d b2=%02x b3=%02x b5=%02x wps=%d%s%n",
                    f, fl.owner, fl.fleetNumber, fl.kindByte, fl.x, fl.y, fl.positionObjectId, ships,
                    fl.ironium, fl.boranium, fl.germanium, fl.population, fl.fuel, fl.battlePlan,
                    fl.byte2 & 0xff, fl.byte3 & 0xff, fl.byte5 & 0xff, fl.waypointCount, dmg);
            } else if (b.typeId == BlockType.FLEET_NAME) {
                // a custom fleet name (block 21) follows its fleet block; Stars-encoded text
                byte[] d = b.getDecryptedData();
                String name;
                try { name = Util.decodeStarsString(Arrays.copyOf(d, b.size)); } catch (Exception e) { name = "?"; }
                System.out.printf("%s   fleetname \"%s\" raw=%s%n", f, name, Util.bytesToString(d, 0, b.size));
            } else if (b instanceof WaypointBlock) {
                WaypointBlock w = (WaypointBlock) b;
                byte[] d = w.getDecryptedData();
                StringBuilder ex = new StringBuilder();
                for (int i = 8; i + 1 < w.size; i += 2) ex.append(i == 8 ? " orders=" : ",").append(String.format("%04x", u16(d, i)));
                System.out.printf("%s   wp x=%d y=%d obj=%d type=%02x warp=%d task=%d%s%n", f,
                    u16(d, 0), u16(d, 2), u16(d, 4), d[7] & 0xff, (d[6] & 0xff) >> 4, d[6] & 15, ex);
            } else if (b instanceof BattlePlanBlock) {
                BattlePlanBlock p = (BattlePlanBlock) b;
                p.decode();
                System.out.printf("%s plan owner=%d k=%d tactic=%d primary=%d secondary=%d who=%d dump=%s name=%s%n",
                    f, p.ownerPlayerId, p.planId, p.tactic, p.primaryTarget, p.secondaryTarget, p.attackWho,
                    p.dumpCargo, p.name);
            } else if (b instanceof PlanetBlock || b instanceof PartialPlanetBlock) {
                PartialPlanetBlock p = (PartialPlanetBlock) b;
                if (!host) // report detail: flag bits 0-6 of the second word
                    System.out.printf("%s seen planet %d owner=%d level=%d starbase=%s env=%s popest=%d defest=%d surface=%s%n", f,
                        p.planetNumber, p.owner, u16(p.getDecryptedData(), 2) & 0x7f, p.hasStarbase, p.hasEnvironmentInfo,
                        p.popEstimate, p.defensesEstimate, p.hasSurfaceMinerals);
                if (p.owner >= 0 || p.hasStarbase)
                    System.out.printf("%s planet %d owner=%d starbase=%s design=%d sbbytes=%s sbdmg=%d minerals=%d/%d/%d pop=%d%n", f,
                        p.planetNumber, p.owner, p.hasStarbase, p.hasStarbase ? p.starbaseDesign : -1,
                        p.starbaseBytes == null ? "-" : Util.bytesToString(p.starbaseBytes, 0, 4),
                        p.starbaseBytes == null ? -1 : ((p.starbaseBytes[0] & 0xff) | (p.starbaseBytes[1] & 0xff) << 8) >> 4,
                        p.ironium, p.boranium, p.germanium, p.population);
                if (host || p.owner >= 0) printPlanetDetail(f, p);
                lastPlanet = p.planetNumber;
            } else if (b instanceof ProductionQueueBlock) {
                // a planet's production queue follows its planet block: per item id,
                // count, percent done of the first unit, kind (as scripts/oracle/hst-edit)
                byte[] d = b.getDecryptedData();
                StringBuilder sb = new StringBuilder();
                for (int i = 0; i + 4 <= b.size; i += 4) {
                    int w0 = u16(d, i), w1 = u16(d, i + 2);
                    sb.append(i == 0 ? " items=" : ",").append(String.format("%d:%d:%d:%d",
                        (w0 >> 10) | ((w1 & 1) << 6), w0 & 0x3ff, (w1 >> 4) & 0x7f, (w1 >> 1) & 7));
                }
                System.out.printf("%s queue planet=%d n=%d%s%n", f, lastPlanet, b.size / 4, sb);
            } else if (b.typeId == 12) {
                // events: one record per message, layout not decoded; printed raw
                byte[] d = b.getDecryptedData();
                StringBuilder h = new StringBuilder();
                for (int i = 0; i < b.size; i++) h.append(String.format("%02x", d[i]));
                System.out.printf("%s events raw=%s%n", f, h);
                printMessages(f, d, b.size);
            } else if (b.typeId == BlockType.OBJECT) {
                System.out.printf("%s %s%n", f, thingString(b.getDecryptedData(), b.size));
            } else if (b.typeId == BlockType.PLANETS) {
                PlanetsBlock p = (PlanetsBlock) b;
                int x = 1000;
                for (int i = 0; i < p.planetsSize; i++) {
                    long v = Util.read32(p.planetsData, 4 * i);
                    int dx = (int) v & 0x3ff, y = (int) (v >> 10) & 0xfff;
                    x += dx;
                    System.out.printf("%s xy planet %d x=%d y=%d%n", f, i, x, y);
                }
            } else if (b instanceof ObjectBlock) {
                StringBuilder hx = new StringBuilder();
                byte[] d = b.getDecryptedData();
                for (int i = 0; i < b.size; i++) hx.append(String.format("%02x", d[i] & 0xff));
                System.out.printf("%s object %s raw=%s%n", f, b.toString().trim().replace('\n', ' '), hx);
            } else if (b.typeId == BlockType.BATTLE) {
                battle = new StringBuilder();
            }
            if (battle != null && (b.typeId == BlockType.BATTLE || b.typeId == BlockType.BATTLE_CONTINUATION)) {
                byte[] d = b.getDecryptedData();
                for (int i = 0; i < b.size; i++) battle.append(String.format("%02x", d[i] & 0xff));
            }
        }
        if (battle != null) printBattle(f, turn, battle.toString());
    }

    // Battle record (block 31 followed by continuation blocks 39), as
    // documented in docs/PARITY.md "Combat": a 14-byte header, one 29-byte
    // record per token, then actions (6 bytes, followed by 8 bytes per hit).
    static void printBattle(String f, int turn, String hex) {
        byte[] r = new byte[hex.length() / 2];
        for (int i = 0; i < r.length; i++) r[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
        int ntok = r[3] & 0xff;
        System.out.printf("%s battle turn=%d id=%#x players=%d mask=%#x length=%d planet=%d x=%d y=%d tokens=%d bytes=%d%n",
            f, turn, u16(r, 0), r[2] & 0xff, u16(r, 4), u16(r, 6), u16(r, 8), u16(r, 10), u16(r, 12), ntok, r.length);
        System.out.printf("%s battlehex %s%n", f, hex);
        int o = 14;
        for (int t = 0; t < ntok; t++, o += 29) {
            int sq = r[o + 5] & 0xff;
            System.out.printf("%s   tok %d obj=%d owner=%d kind=%d design=%d sq=(%d,%d) init=%d winit=%d..%d b9=%d b10=%d jam=%d comp=%d cap=%d defl=%d mass=%d shield=%d ships=%d dmg=%d/%d%% w23=%04x w25=%04x w27=%04x%n",
                f, t, u16(r, o), r[o + 2] & 0xff, r[o + 3] & 0xff, r[o + 4] & 0xff, sq & 15, sq >> 4,
                r[o + 6] & 0xff, r[o + 7] & 0xff, r[o + 8] & 0xff, r[o + 9] & 0xff, r[o + 10] & 0xff,
                r[o + 11] & 0xff, r[o + 12] & 0xff, r[o + 13] & 0xff, r[o + 14] & 0xff,
                u16(r, o + 15), u16(r, o + 17), u16(r, o + 19), u16(r, o + 21) >> 7, u16(r, o + 21) & 0x7f,
                u16(r, o + 23), u16(r, o + 25), u16(r, o + 27));
        }
        int end = Math.min(r.length, u16(r, 6) == 0 ? r.length : u16(r, 6));
        while (o + 6 <= end) {
            int tok = r[o] & 0xff, sq = r[o + 1] & 0xff, nh = u16(r, o + 2), w = u16(r, o + 4);
            o += 6;
            System.out.printf("%s   act round=%d tok=%d %s nhits=%d w=%04x%n", f, w & 15, tok,
                sq == 0xff ? "to=off" : String.format("to=(%d,%d)", sq & 15, sq >> 4), nh, w);
            for (int h = 0; h < nh && o + 8 <= r.length; h++, o += 8) {
                int sp = u16(r, o + 4), dmg = u16(r, o + 6);
                System.out.printf("%s     hit tok=%d flags=%02x kills=%d shielddmg=%d dmg=%d/%d%%%n", f,
                    r[o] & 0xff, r[o + 1] & 0xff, u16(r, o + 2), (sp & 0x1fff) << (2 * (sp >> 13)), dmg >> 7, dmg & 0x7f);
            }
        }
        if (o != r.length) System.out.printf("%s   trailing=%d%n", f, r.length - o);
    }

    // Takeover detail: installations, carry byte, environment.
    static void printPlanetDetail(String f, PartialPlanetBlock p) {
        StringBuilder sb = new StringBuilder();
        if (p.canSeeEnvironment())
            sb.append(String.format(" conc=%d/%d/%d env=%d/%d/%d", p.ironiumConc, p.boraniumConc, p.germaniumConc,
                p.gravity, p.temperature, p.radiation));
        if (p.isTerraformed) sb.append(String.format(" orig=%d/%d/%d", p.origGravity, p.origTemperature, p.origRadiation));
        if (p.hasSurfaceMinerals) sb.append(String.format(" surface=%d/%d/%d pop=%d", p.ironium, p.boranium, p.germanium, p.population));
        if (p.hasInstallations)
            sb.append(String.format(" excess=%d mines=%d factories=%d defenses=%d scanner=%d leftover=%b",
                p.excessPop, p.mines, p.factories,
                (p.defenses & 0xff) | ((p.unknownInstallationsByte & 0x0f) << 8),
                ((p.unknownInstallationsByte >> 4) & 15) | (p.hasScanner ? 0 : 16), p.contributeOnlyLeftoverResourcesToResearch));
        // route destination word (planet id + 1 in bits 0-9 per the decomp; 0 = none)
        if (p.hasRoute) sb.append(String.format(" route=%04x", p.routeShort));
        if (sb.length() > 0) System.out.printf("%s pdetail %d owner=%d%s%n", f, p.planetNumber, p.owner, sb);
    }

    static int u16(byte[] b, int o) {
        return (b[o] & 0xff) | ((b[o + 1] & 0xff) << 8);
    }

    // ----------------------------------------------------------------- build

    static class FleetSpec {
        int owner, id, x, y, fuel, plan, planet = -1;
        int wp0Fleet = -1;  // waypoint 0 targets this fleet id (number | owner << 9) when >= 0
        long[] cargo = new long[4];
        int[] ships = new int[16];
        int[] dmg = new int[16];
        // waypoints after waypoint 0: x, y, obj, type, warp; tasks per waypoint (0 = waypoint 0)
        List<int[]> wps = new ArrayList<>();
        Map<Integer, Integer> task = new HashMap<>();
        Map<Integer, int[]> orders = new HashMap<>();
    }

    // Waypoint task: returns the task number and fills ord (5 transport words) when needed.
    static int parseTask(String[] t, int i, int[] ord) throws Exception {
        switch (t[i]) {
            case "colonize": return 2;
            case "scrap": return 5;
            case "mine": return 3;
            case "merge": return 4;
            case "transfer": {
                // transfer fleet: one word, the recipient as an index over the other players
                ord[0] = Integer.parseInt(t[i + 1]);
                return 9;
            }
            case "unload": ord[3] = 2 << 12; return 1;
            case "lay": {
                // lay mines: one word, the years counter (5 = indefinitely)
                ord[0] = t.length > i + 1 && t[i + 1].matches("\\d+") ? Integer.parseInt(t[i + 1]) : 5;
                return 6;
            }
            case "transport": {
                String[] w = t[i + 1].split(",");
                if (w.length != 5) throw new Exception("transport needs 5 A:V entries");
                for (int k = 0; k < 5; k++) {
                    if (w[k].equals("-")) continue;
                    String[] av = w[k].split(":");
                    ord[k] = Integer.parseInt(av[0]) << 12 | (Integer.parseInt(av[1]) & 0xfff);
                }
                return 1;
            }
            default: throw new Exception("unknown task " + t[i]);
        }
    }

    static DesignBlock parseDesign(boolean starbase, int n, String spec) throws Exception {
        String[] ns = spec.split("=", 2);
        if (ns.length != 2) throw new Exception("design needs '= NAME'");
        String[] parts = ns[0].split(",");
        int hull = Items.getHullIdOfUserString(parts[0].trim());
        DesignBlock d = new DesignBlock();
        d.isFullDesign = true;
        d.isStarbase = starbase;
        d.designNumber = n;
        d.hullId = hull;
        d.pic = 4 * hull;
        if (hull == 29) d.pic = 4 * 31;
        else if (hull == 31) d.pic = 4 * 29;
        d.armor = Items.ships[hull].armor;
        d.slotCount = Items.ships[hull].slotCount;
        if (parts.length - 1 > d.slotCount) throw new Exception("too many slots for " + parts[0]);
        for (int s = 0; s < d.slotCount; s++) {
            DesignBlock.Slot slot = new DesignBlock.Slot();
            String p = s + 1 < parts.length ? parts[s + 1].trim() : "empty";
            if (!p.equalsIgnoreCase("empty")) {
                int count = -1;
                int sp = p.indexOf(' ');
                if (sp > 0 && p.substring(0, sp).matches("\\d+")) {
                    count = Integer.parseInt(p.substring(0, sp));
                    p = p.substring(sp + 1).trim();
                }
                Integer key = Items.itemsByName.get(p);
                if (key == null) {
                    // StarsAPI abbreviations, e.g. "beta", "bsc"
                    DesignBlock.Slot ab = Items.getSlotOfUserString(p);
                    String full = null;
                    for (Map.Entry<String, Integer> e : Items.itemsByName.entrySet())
                        if ((e.getValue() >> 8) == ab.category && e.getKey().equalsIgnoreCase(p)) full = e.getKey();
                    throw new Exception("use the full item name for '" + p + "'" + (full == null ? "" : " (" + full + ")"));
                }
                slot.category = key >> 8;
                slot.itemId = key & 0xff;
                int size = starbase ? -1 : Items.ships[hull].slotSizes[s];
                slot.count = count >= 0 ? count : (size > 0 ? size : 1);
                if (size > 0 && slot.count > size) throw new Exception(p + " x" + slot.count + " exceeds slot " + s + " size " + size);
                Integer armor = Items.itemArmors.get(key);
                if (armor != null) d.armor += slot.count * armor;
            }
            d.slots.add(slot);
        }
        d.nameBytes = Util.encodeStarsString(ns[1].trim());
        d.encode();
        d.decode();
        return d;
    }

    static void build(String base, String spec, String out) throws Exception {
        Decryptor dec = new Decryptor();
        List<Block> blocks = dec.readFile(base);
        Map<String, Integer> tech = new HashMap<>();
        Map<Integer, Integer> lrts = new HashMap<>(), research = new HashMap<>(), prts = new HashMap<>();
        Map<Integer, byte[]> habs = new HashMap<>();
        Map<Integer, Integer> fields = new HashMap<>(), defLeftover = new HashMap<>(), mts = new HashMap<>();
        Map<Integer, byte[]> queues = new HashMap<>(); // planet -> queue block data (empty = none)
        Map<Integer, List<Integer>> defQueues = new HashMap<>();
        Map<Integer, TreeMap<Integer, DesignBlock>> shipDesigns = new TreeMap<>(), sbDesigns = new TreeMap<>();
        Map<Integer, BattlePlanBlock> plans = new HashMap<>();
        Map<Integer, Map<Integer, Integer>> relations = new HashMap<>();
        List<FleetSpec> fleets = new ArrayList<>();
        Map<Integer, int[]> planetSpecs = new HashMap<>(); // N -> {owner, pop, starbase, scanner}; -2 = keep, -1 = none
        Map<Integer, Map<String, String>> planetSets = new HashMap<>();
        TreeMap<Integer, byte[]> things = new TreeMap<>(); // id -> 18-byte record
        int lineNo = 0;
        for (String raw : Files.readAllLines(Paths.get(spec))) {
            lineNo++;
            String line = raw.replaceAll("#.*", "").trim();
            if (line.isEmpty()) continue;
            String[] t = line.split("\\s+");
            try {
                switch (t[0]) {
                    case "tech": tech.put(t[1] + " " + t[2], Integer.parseInt(t[3])); break;
                    case "lrt": lrts.put(Integer.parseInt(t[1]), Integer.decode(t[2])); break;
                    case "prt": prts.put(Integer.parseInt(t[1]), Integer.parseInt(t[2])); break;
                    case "hab": {
                        String[] h = t[2].split(",");
                        if (h.length != 9) throw new Exception("hab needs 9 values");
                        byte[] hb = new byte[9];
                        for (int i = 0; i < 9; i++) hb[i] = (byte) Integer.parseInt(h[i]);
                        habs.put(Integer.parseInt(t[1]), hb);
                        break;
                    }
                    case "research": research.put(Integer.parseInt(t[1]), Integer.parseInt(t[2])); break;
                    case "field": fields.put(Integer.parseInt(t[1]), Arrays.asList(TECH).indexOf(t[2])); break;
                    case "defleftover": defLeftover.put(Integer.parseInt(t[1]), Integer.parseInt(t[2])); break;
                    case "mt": {
                        int v = Integer.parseInt(t[2].replaceFirst("^0x", ""), 16);
                        if (v < 0 || v > 0xffff) throw new Exception("mt: 16-bit mask expected");
                        mts.put(Integer.parseInt(t[1]), v);
                        break;
                    }
                    case "queue": queues.put(Integer.parseInt(t[1]), parseQueue(t[2])); break;
                    case "defqueue": {
                        List<Integer> q = new ArrayList<>();
                        if (!t[2].equals("none"))
                            for (String e : t[2].split(",")) {
                                String[] ic = e.split(":");
                                int id = Integer.parseInt(ic[0]), c = Integer.parseInt(ic[1]);
                                if (id < 0 || id > 63 || c < 0 || c > 1023) throw new Exception("defqueue: bad item " + e);
                                q.add(id | c << 6);
                            }
                        if (q.size() > 12) throw new Exception("defqueue: at most 12 items");
                        defQueues.put(Integer.parseInt(t[1]), q);
                        break;
                    }
                    case "relation":
                        relations.computeIfAbsent(Integer.parseInt(t[1]), k -> new TreeMap<>())
                            .put(Integer.parseInt(t[2]), Integer.parseInt(t[3]));
                        break;
                    case "design": case "sbdesign": {
                        int p = Integer.parseInt(t[1]), n = Integer.parseInt(t[2]);
                        String rest = line.replaceFirst("^\\S+\\s+\\S+\\s+\\S+\\s+", "");
                        boolean sb = t[0].equals("sbdesign");
                        (sb ? sbDesigns : shipDesigns).computeIfAbsent(p, k -> new TreeMap<>())
                            .put(n, parseDesign(sb, n, rest));
                        break;
                    }
                    case "plan": {
                        BattlePlanBlock bp = new BattlePlanBlock();
                        bp.ownerPlayerId = Integer.parseInt(t[1]);
                        bp.planId = Integer.parseInt(t[2]);
                        bp.tactic = Integer.parseInt(t[3]);
                        bp.primaryTarget = Integer.parseInt(t[4]);
                        bp.secondaryTarget = Integer.parseInt(t[5]);
                        bp.attackWho = Integer.parseInt(t[6]);
                        bp.dumpCargo = t.length > 7 && t[7].equals("dump");
                        bp.name = line.split("=", 2)[1].trim();
                        bp.encode();
                        bp.setData(bp.getDecryptedData(), bp.size);
                        plans.put(bp.ownerPlayerId * 16 + bp.planId, bp);
                        break;
                    }
                    case "fleet": fleets.add(parseFleet(t)); break;
                    case "fleets": {
                        // fleets OWNER FROM-TO <fleet tokens>: one fleet per id in the range
                        String[] r = t[2].split("-");
                        for (int id = Integer.parseInt(r[0]); id <= Integer.parseInt(r[r.length - 1]); id++) {
                            String[] one = t.clone();
                            one[2] = "" + id;
                            fleets.add(parseFleet(one));
                        }
                        break;
                    }
                    case "thing": {
                        byte[] r = parseThing(t);
                        int id = u16(r, 0);
                        if (things.put(id, r) != null) throw new Exception("duplicate thing id " + id);
                        break;
                    }
                    case "planetset": {
                        Map<String, String> kv = planetSets.computeIfAbsent(Integer.parseInt(t[1]), k -> new LinkedHashMap<>());
                        for (int i = 2; i < t.length; i++) {
                            String[] e = t[i].split("=", 2);
                            if (e.length != 2) throw new Exception("planetset: KEY=V expected, got " + t[i]);
                            kv.put(e[0], e[1]);
                        }
                        break;
                    }
                    case "planet": {
                        int[] ps = {-2, -2, -2, -2};
                        for (int i = 2; i + 1 < t.length; i += 2) {
                            int v = t[i + 1].equals("none") ? -1 : t[i + 1].equals("on") ? 1 : Integer.parseInt(t[i + 1]);
                            switch (t[i]) {
                                case "owner": ps[0] = v; break;
                                case "pop": ps[1] = v; break;
                                case "starbase": ps[2] = v; break;
                                case "scanner": ps[3] = v; break;
                                default: throw new Exception("planet: unknown key " + t[i]);
                            }
                        }
                        planetSpecs.put(Integer.parseInt(t[1]), ps);
                        break;
                    }
                    default: throw new Exception("unknown directive " + t[0]);
                }
            } catch (Exception e) {
                throw new Exception(spec + ":" + lineNo + ": " + e.getMessage(), e);
            }
        }

        // Pass 1: classify existing blocks.
        List<PlayerBlock> players = new ArrayList<>();
        Map<Integer, byte[]> fleetTemplate = new HashMap<>();
        Map<Integer, PartialPlanetBlock> homeworld = new HashMap<>();
        Map<Integer, List<DesignBlock>> oldShip = new TreeMap<>(), oldSb = new TreeMap<>();
        int shipSeen = 0, sbSeen = 0;
        for (Block b : blocks) {
            if (b instanceof PlayerBlock) players.add((PlayerBlock) b);
            if (b instanceof DesignBlock) {
                DesignBlock d = (DesignBlock) b;
                int seen = d.isStarbase ? sbSeen++ : shipSeen++;
                for (PlayerBlock p : players) {
                    int n = d.isStarbase ? p.starbaseDesignCount : p.shipDesignCount;
                    if (seen < n) {
                        (d.isStarbase ? oldSb : oldShip).computeIfAbsent(p.playerNumber, k -> new ArrayList<>()).add(d);
                        break;
                    }
                    seen -= n;
                }
            }
            if (b instanceof PartialPlanetBlock) {
                PartialPlanetBlock pl = (PartialPlanetBlock) b;
                if (pl.isHomeworld && pl.owner >= 0) homeworld.putIfAbsent(pl.owner, pl);
            }
            if (b instanceof PartialFleetBlock) {
                PartialFleetBlock fl = (PartialFleetBlock) b;
                fleetTemplate.putIfAbsent(fl.owner, Arrays.copyOf(fl.getDecryptedData(), fl.size));
            }
        }

        // Final design lists per player.
        Map<Integer, Collection<DesignBlock>> ship = new TreeMap<>(), sbs = new TreeMap<>();
        for (PlayerBlock p : players) {
            int k = p.playerNumber;
            ship.put(k, shipDesigns.containsKey(k) ? shipDesigns.get(k).values() : oldShip.getOrDefault(k, List.of()));
            sbs.put(k, sbDesigns.containsKey(k) ? sbDesigns.get(k).values() : oldSb.getOrDefault(k, List.of()));
        }

        // Fleets and their waypoints.
        fleets.sort(Comparator.comparingInt((FleetSpec f) -> f.owner).thenComparingInt(f -> f.id));
        List<Block> newFleets = new ArrayList<>();
        Map<Integer, Integer> fleetCount = new HashMap<>();
        Set<Integer> ids = new HashSet<>();
        for (FleetSpec fs : fleets) {
            if (!ids.add(fs.owner * 1024 + fs.id)) throw new Exception("duplicate fleet " + fs.owner + "/" + fs.id);
            byte[] tpl = fleetTemplate.getOrDefault(fs.owner, fleetTemplate.get(0));
            FleetBlock fl = new FleetBlock();
            fl.setDecryptedData(Arrays.copyOf(tpl, tpl.length), tpl.length);
            fl.decode();
            fl.fleetNumber = fs.id;
            fl.owner = fs.owner;
            fl.positionObjectId = fs.planet >= 0 ? fs.planet : 0xFFFF;
            fl.x = fs.x;
            fl.y = fs.y;
            fl.shipTypes = 0;
            boolean big = false;
            Set<Integer> have = new HashSet<>();
            for (DesignBlock d : ship.get(fs.owner)) have.add(d.designNumber);
            for (int i = 0; i < 16; i++) {
                fl.shipCount[i] = fs.ships[i];
                if (fs.ships[i] > 0) {
                    if (!have.contains(i)) throw new Exception("fleet " + fs.owner + "/" + fs.id + ": no design " + i);
                    fl.shipTypes |= 1 << i;
                }
                if (fs.ships[i] > 255) big = true;
            }
            fl.byte5 = (byte) (big ? (fl.byte5 & ~8) : (fl.byte5 | 8));
            fl.ironium = fs.cargo[0];
            fl.boranium = fs.cargo[1];
            fl.germanium = fs.cargo[2];
            fl.population = fs.cargo[3];
            fl.fuel = fs.fuel;
            fl.damagedShipTypes = 0;
            for (int i = 0; i < 16; i++) {
                fl.damagedShipInfo[i] = fs.dmg[i];
                if (fs.dmg[i] != 0) fl.damagedShipTypes |= 1 << i;
            }
            fl.battlePlan = fs.plan;
            fl.waypointCount = 1 + fs.wps.size();
            fl.encode();
            fl.setData(fl.getDecryptedData(), fl.size);
            newFleets.add(fl);
            List<int[]> all = new ArrayList<>();
            all.add(fs.wp0Fleet >= 0 ? new int[]{fs.x, fs.y, fs.wp0Fleet, 0x12, 0}
                : fs.planet >= 0 ? new int[]{fs.x, fs.y, fs.planet, 0x11, 0} : new int[]{fs.x, fs.y, 0, 0x14, 0});
            all.addAll(fs.wps);
            for (int w = 0; w < all.size(); w++) {
                int[] wp = all.get(w);
                WaypointBlock wb = new WaypointBlock();
                wb.x = wp[0]; wb.y = wp[1];
                wb.positionObject = wp[2];
                wb.positionObjectType = wp[3];
                wb.warp = wp[4];
                wb.waypointTask = fs.task.getOrDefault(w, 0);
                if (wb.waypointTask == 1) {
                    // transport: five order words (Ir, Bo, Ge, colonists, fuel), action << 12 | value
                    for (int o : fs.orders.get(w)) { wb.additionalBytes.add((byte) o); wb.additionalBytes.add((byte) (o >> 8)); }
                } else if (wb.waypointTask == 6 || wb.waypointTask == 9) {
                    int o = fs.orders.get(w)[0];
                    wb.additionalBytes.add((byte) o); wb.additionalBytes.add((byte) (o >> 8));
                }
                wb.encode();
                newFleets.add(wb);
            }
            fleetCount.merge(fs.owner, 1, Integer::sum);
        }

        // Player blocks: tech, design and fleet counts, relations.
        for (PlayerBlock p : players) {
            int k = p.playerNumber;
            for (Map.Entry<String, Integer> e : tech.entrySet()) {
                String[] pf = e.getKey().split(" ");
                if (Integer.parseInt(pf[0]) != k) continue;
                int i = Arrays.asList(TECH).indexOf(pf[1]);
                if (i < 0) throw new Exception("unknown tech field " + pf[1]);
                p.fullDataBytes[0x12 + i] = (byte) (int) e.getValue();
            }
            if (lrts.containsKey(k)) {
                p.fullDataBytes[0x46] = (byte) (lrts.get(k) & 0xff);
                p.fullDataBytes[0x47] = (byte) (lrts.get(k) >> 8);
            }
            if (prts.containsKey(k)) p.fullDataBytes[0x44] = (byte) (int) prts.get(k);
            if (habs.containsKey(k)) System.arraycopy(habs.get(k), 0, p.fullDataBytes, 8, 9);
            if (research.containsKey(k)) p.fullDataBytes[0x30] = (byte) (int) research.get(k);
            if (fields.containsKey(k)) {
                if (fields.get(k) < 0) throw new Exception("field: unknown tech field");
                p.fullDataBytes[0x31] = (byte) ((p.fullDataBytes[0x31] & 0xf0) | fields.get(k));
            }
            if (mts.containsKey(k)) Util.write16(p.fullDataBytes, 0x4a, mts.get(k));
            if (defLeftover.containsKey(k))
                p.fullDataBytes[0x4e] = (byte) ((p.fullDataBytes[0x4e] & ~1) | (defLeftover.get(k) & 1));
            if (defQueues.containsKey(k)) {
                List<Integer> q = defQueues.get(k);
                for (int i = 0x4f; i < 0x68; i++) p.fullDataBytes[i] = 0;
                p.fullDataBytes[0x4f] = (byte) q.size();
                for (int i = 0; i < q.size(); i++) Util.write16(p.fullDataBytes, 0x50 + 2 * i, q.get(i));
            }
            p.shipDesignCount = ship.get(k).size();
            p.starbaseDesignCount = sbs.get(k).size();
            p.fleets = fleetCount.getOrDefault(k, 0);
            if (relations.containsKey(k)) {
                Map<Integer, Integer> rel = relations.get(k);
                int len = Math.max(p.playerRelations.length, Collections.max(rel.keySet()) + 1);
                len = Math.max(len, players.size());
                byte[] r = Arrays.copyOf(p.playerRelations, len);
                for (Map.Entry<Integer, Integer> e : rel.entrySet()) r[e.getKey()] = (byte) (int) e.getValue();
                p.playerRelations = r;
            }
            p.encode();
            p.setData(p.getDecryptedData(), p.size);
            p.decode();
        }

        // Pass 2: rebuild the block list.
        List<Block> result = new ArrayList<>();
        boolean shipDone = false, fleetsDone = false, sbDone = false, thingsDone = false;
        int lastPlanet = -1;
        Set<Integer> queuesDone = new HashSet<>();
        for (Block b : blocks) {
            // a planet's production queue block follows its planet block
            if (b instanceof ProductionQueueBlock && queues.containsKey(lastPlanet)) continue;
            if (b instanceof DesignBlock) {
                DesignBlock d = (DesignBlock) b;
                if (!d.isStarbase && !shipDone) {
                    for (Collection<DesignBlock> c : ship.values()) result.addAll(c);
                    shipDone = true;
                }
                if (d.isStarbase) {
                    if (!fleetsDone) { result.addAll(newFleets); fleetsDone = true; }
                    if (!sbDone) { for (Collection<DesignBlock> c : sbs.values()) result.addAll(c); sbDone = true; }
                }
                continue;
            }
            if (b instanceof PartialFleetBlock || b instanceof WaypointBlock) continue;
            if (b.typeId == BlockType.OBJECT && !things.isEmpty()) continue;
            if (!things.isEmpty() && !thingsDone && (b instanceof BattlePlanBlock || b.typeId == BlockType.FILE_FOOTER)) {
                if (!fleetsDone) { result.addAll(newFleets); fleetsDone = true; }
                ObjectBlock cb = new ObjectBlock();
                byte[] c = new byte[2];
                Util.write16(c, 0, things.size());
                cb.setDecryptedData(c, 2);
                result.add(cb);
                for (byte[] r : things.values()) {
                    ObjectBlock ob = new ObjectBlock();
                    ob.setDecryptedData(Arrays.copyOf(r, 18), 18);
                    result.add(ob);
                }
                thingsDone = true;
            }
            if (b instanceof PartialPlanetBlock && planetSpecs.containsKey(((PartialPlanetBlock) b).planetNumber)) {
                PartialPlanetBlock pl = (PartialPlanetBlock) b;
                int[] ps = planetSpecs.remove(pl.planetNumber);
                int owner = ps[0] >= 0 ? ps[0] : pl.owner;
                PartialPlanetBlock hw = homeworld.get(owner);
                if (hw == null) throw new Exception("planet " + pl.planetNumber + ": no homeworld for player " + owner);
                if (ps[0] >= 0 && pl.owner != owner) {
                    pl.owner = owner;
                    pl.isHomeworld = false;
                    pl.hasEnvironmentInfo = hw.hasEnvironmentInfo;
                    pl.bitWhichIsOffForRemoteMiningAndRobberBaron = hw.bitWhichIsOffForRemoteMiningAndRobberBaron;
                    pl.hasSurfaceMinerals = true;
                    pl.hasInstallations = true;
                    pl.excessPop = 0; pl.mines = 0; pl.factories = 0; pl.defenses = 0;
                    pl.unknownInstallationsByte = hw.unknownInstallationsByte;
                    pl.hasScanner = false;
                    pl.contributeOnlyLeftoverResourcesToResearch = false;
                    if (pl.population == 0) pl.population = 100;
                }
                if (ps[1] >= 0) pl.population = ps[1];
                pl.popEstimate = (int) Math.min(4095, pl.population * 100 / 400);
                if (ps[2] == -1) pl.hasStarbase = false;
                else if (ps[2] >= 0) {
                    if (hw.starbaseBytes == null) throw new Exception("player " + owner + "'s homeworld has no starbase to copy");
                    pl.hasStarbase = true;
                    pl.starbaseBytes = Arrays.copyOf(hw.starbaseBytes, 4);
                    pl.starbaseBytes[0] = (byte) ((pl.starbaseBytes[0] & 0xF0) | ps[2]);
                    pl.starbaseDesign = ps[2];
                }
                if (ps[3] == -1) { // scanner id 31: high nibble of byte 5 and bit 0 of byte 6
                    pl.unknownInstallationsByte |= (byte) 0xF0;
                    pl.hasScanner = false;
                } else if (ps[3] == 1) {
                    pl.unknownInstallationsByte &= 0x0F;
                    pl.hasScanner = true;
                }
                pl.encode();
                pl.setData(pl.getDecryptedData(), pl.size);
                pl.decode();
            }
            if (b instanceof PartialPlanetBlock && planetSets.containsKey(((PartialPlanetBlock) b).planetNumber))
                applyPlanetSet((PartialPlanetBlock) b, planetSets.remove(((PartialPlanetBlock) b).planetNumber));
            if (b instanceof BattlePlanBlock) {
                BattlePlanBlock bp = (BattlePlanBlock) b;
                bp.decode();
                BattlePlanBlock rep = plans.remove(bp.ownerPlayerId * 16 + bp.planId);
                if (rep != null) b = rep;
                // new plans for this player go after its last existing plan
            }
            if (b.typeId == BlockType.FILE_FOOTER) {
                if (!fleetsDone) { result.addAll(newFleets); fleetsDone = true; }
                List<BattlePlanBlock> rest = new ArrayList<>(plans.values());
                rest.sort(Comparator.comparingInt(x -> x.ownerPlayerId * 16 + x.planId));
                if (!rest.isEmpty()) {
                    // insert remaining plans after the owner's last plan
                    for (BattlePlanBlock bp : rest) {
                        int at = result.size();
                        for (int i = 0; i < result.size(); i++) {
                            Block x = result.get(i);
                            if (x instanceof BattlePlanBlock && ((BattlePlanBlock) x).ownerPlayerId <= bp.ownerPlayerId) at = i + 1;
                        }
                        result.add(at, bp);
                    }
                    plans.clear();
                }
            }
            result.add(b);
            if (b instanceof PartialPlanetBlock) {
                PartialPlanetBlock pl = (PartialPlanetBlock) b;
                lastPlanet = pl.planetNumber;
                byte[] q = queues.get(lastPlanet);
                if (q != null) {
                    if (pl.owner < 0) throw new Exception("queue: planet " + lastPlanet + " has no owner");
                    if (q.length > 0) {
                        ProductionQueueBlock pq = new ProductionQueueBlock();
                        pq.setDecryptedData(Arrays.copyOf(q, q.length), q.length);
                        pq.setData(q.clone(), q.length);
                        result.add(pq);
                    }
                    queuesDone.add(lastPlanet);
                }
            }
        }
        if (!queuesDone.containsAll(queues.keySet())) throw new Exception("queue: no planet " + queues.keySet());
        if (!plans.isEmpty()) throw new Exception("unplaced plans");
        if (!planetSets.isEmpty()) throw new Exception("planetset: no planet " + planetSets.keySet());
        dec.writeBlocks(out, result, false);
        System.out.printf("wrote %s: %d fleets%n", out, fleets.size());
    }

    // Production queue items: two little-endian words per item, as the game stores
    // them (and scripts/oracle/hst-edit writes them): w0 = (id & 63) << 10 | count,
    // w1 = pct << 4 | kind << 1 | id >> 6.
    static byte[] parseQueue(String spec) throws Exception {
        if (spec.equals("none")) return new byte[0];
        String[] items = spec.split(",");
        byte[] d = new byte[items.length * 4];
        for (int j = 0; j < items.length; j++) {
            String[] f = items[j].split(":");
            if (f.length != 3 && f.length != 4) throw new Exception("queue: ID:COUNT[:PCT]:KIND expected, got " + items[j]);
            int id = Integer.parseInt(f[0]), cnt = Integer.parseInt(f[1]);
            int pct = f.length == 4 ? Integer.parseInt(f[2]) : 0, kind = Integer.parseInt(f[f.length - 1]);
            if (id < 0 || id > 127 || cnt < 0 || cnt > 1023 || pct < 0 || pct > 100 || kind < 0 || kind > 7)
                throw new Exception("queue: bad item " + items[j]);
            Util.write16(d, 4 * j, ((id & 0x3f) << 10) | cnt);
            Util.write16(d, 4 * j + 2, (pct << 4) | (kind << 1) | (id >> 6));
        }
        return d;
    }

    static void applyPlanetSet(PartialPlanetBlock pl, Map<String, String> kv) throws Exception {
        for (Map.Entry<String, String> e : kv.entrySet()) {
            String k = e.getKey(), v = e.getValue();
            String[] three = v.split(",");
            boolean inst = k.equals("mines") || k.equals("factories") || k.equals("defenses") || k.equals("excess") || k.equals("scanner");
            if (inst && !pl.hasInstallations) throw new Exception("planetset " + pl.planetNumber + ": no installations (owned planets only)");
            if ((k.equals("fe") || k.equals("bo") || k.equals("ge")) && !pl.hasSurfaceMinerals)
                throw new Exception("planetset " + pl.planetNumber + ": no surface minerals");
            if ((k.equals("conc") || k.equals("env") || k.equals("orig")) && three.length != 3)
                throw new Exception("planetset " + k + " needs 3 values");
            switch (k) {
                case "mines": pl.mines = Integer.parseInt(v); break;
                case "factories": pl.factories = Integer.parseInt(v); break;
                case "defenses": {
                    int d = Integer.parseInt(v);
                    pl.defenses = d & 0xff;
                    pl.unknownInstallationsByte = (byte) ((pl.unknownInstallationsByte & 0xf0) | ((d >> 8) & 0x0f));
                    break;
                }
                case "excess": pl.excessPop = Integer.parseInt(v); break;
                case "scanner": {
                    // planetary scanner id 0-31 (31 = none): bits 0-3 in the high nibble of
                    // installations byte 5, bit 4 = the "no scanner" bit of byte 6
                    int id = Integer.parseInt(v);
                    pl.unknownInstallationsByte = (byte) ((pl.unknownInstallationsByte & 0x0f) | ((id & 15) << 4));
                    pl.hasScanner = (id & 16) == 0;
                    break;
                }
                case "sbdmg": {
                    // starbase damage units (1/500 of armor): bits 4-15 of starbase word 0
                    if (pl.starbaseBytes == null) throw new Exception("planetset " + pl.planetNumber + ": no starbase");
                    int w = (pl.starbaseBytes[0] & 0xff) | (pl.starbaseBytes[1] & 0xff) << 8;
                    w = (w & 0x000f) | (Integer.parseInt(v) & 0x0fff) << 4;
                    pl.starbaseBytes[0] = (byte) w; pl.starbaseBytes[1] = (byte) (w >> 8);
                    break;
                }
                case "driver": {
                    // driver=DEST[,WARP]: mass-driver packet destination (planet number, stored
                    // +1 in bits 0-9 of starbase word 1) and the chosen packet warp (bits 10-13,
                    // warp - 4; default 0, which launches at the driver's own warp)
                    if (pl.starbaseBytes == null) throw new Exception("planetset " + pl.planetNumber + ": no starbase");
                    String[] dw = v.split(",");
                    int w = (Integer.parseInt(dw[0]) + 1) & 0x3ff;
                    if (dw.length > 1) w |= ((Integer.parseInt(dw[1]) - 4) & 15) << 10;
                    pl.starbaseBytes[2] = (byte) w; pl.starbaseBytes[3] = (byte) (w >> 8);
                    break;
                }
                case "route":
                    // route=DEST (planet number; stored as DEST + 1), route=none, or route=raw:HEX (whole word)
                    if (v.equals("none")) { pl.hasRoute = false; pl.routeShort = 0; }
                    else {
                        pl.hasRoute = true;
                        pl.routeShort = v.startsWith("raw:") ? Integer.parseInt(v.substring(4), 16) : Integer.parseInt(v) + 1;
                    }
                    break;
                case "fe": pl.ironium = Long.parseLong(v); break;
                case "bo": pl.boranium = Long.parseLong(v); break;
                case "ge": pl.germanium = Long.parseLong(v); break;
                case "conc":
                    pl.ironiumConc = Integer.parseInt(three[0]); pl.boraniumConc = Integer.parseInt(three[1]);
                    pl.germaniumConc = Integer.parseInt(three[2]); break;
                case "env":
                    pl.gravity = Integer.parseInt(three[0]); pl.temperature = Integer.parseInt(three[1]);
                    pl.radiation = Integer.parseInt(three[2]); break;
                case "orig":
                    if (!pl.isTerraformed) {
                        pl.isTerraformed = true;
                        pl.origGravity = pl.gravity; pl.origTemperature = pl.temperature; pl.origRadiation = pl.radiation;
                    }
                    pl.origGravity = Integer.parseInt(three[0]); pl.origTemperature = Integer.parseInt(three[1]);
                    pl.origRadiation = Integer.parseInt(three[2]); break;
                default: throw new Exception("planetset: unknown key " + k);
            }
        }
        pl.encode();
        pl.setData(pl.getDecryptedData(), pl.size);
        pl.decode();
    }

    // One 18-byte universe-object record (docs/ORACLE.md "Universe objects").
    static byte[] parseThing(String[] t) throws Exception {
        byte[] r = new byte[18];
        String kind = t[1];
        if (kind.equals("raw")) {
            if (t[2].length() != 36) throw new Exception("thing raw needs 36 hex digits");
            for (int i = 0; i < 18; i++) r[i] = (byte) Integer.parseInt(t[2].substring(2 * i, 2 * i + 2), 16);
            return r;
        }
        int i;
        switch (kind) {
            case "minefield": {
                int owner = Integer.parseInt(t[2]), num = Integer.parseInt(t[3]);
                Util.write16(r, 0, owner << 9 | num);
                Util.write16(r, 2, Integer.parseInt(t[4]));
                Util.write16(r, 4, Integer.parseInt(t[5]));
                Util.write32(r, 6, Long.parseLong(t[6]));
                for (i = 7; i < t.length; i++) {
                    switch (t[i]) {
                        case "kind": r[12] = (byte) Arrays.asList("std", "heavy", "bump").indexOf(t[++i]); if (r[12] < 0) throw new Exception("kind std|heavy|bump"); break;
                        case "det": r[13] = 1; break;
                        case "known": Util.write16(r, 10, Integer.decode(t[++i])); break;
                        case "seen": Util.write16(r, 14, Integer.decode(t[++i])); break;
                        default: throw new Exception("minefield: unknown token " + t[i]);
                    }
                }
                return r;
            }
            case "packet": {
                int owner = Integer.parseInt(t[2]), num = Integer.parseInt(t[3]);
                int dest = Integer.parseInt(t[6]), warp = Integer.parseInt(t[7]);
                long ir = Long.parseLong(t[8]), bo = Long.parseLong(t[9]), ge = Long.parseLong(t[10]);
                int cls = 0, moved = 0, b15 = 0;
                for (i = 11; i < t.length; i++) {
                    switch (t[i]) {
                        case "class": cls = Integer.parseInt(t[++i]); break;
                        case "moved": moved = 1; break;
                        case "bit15": b15 = 1; break;
                        default: throw new Exception("packet: unknown token " + t[i]);
                    }
                }
                Util.write16(r, 0, 1 << 13 | owner << 9 | num);
                Util.write16(r, 2, Integer.parseInt(t[4]));
                Util.write16(r, 4, Integer.parseInt(t[5]));
                Util.write16(r, 6, (dest & 0x3ff) | ((warp - 4) & 15) << 10 | moved << 14 | b15 << 15);
                Util.write16(r, 8, (int) ir); Util.write16(r, 10, (int) bo); Util.write16(r, 12, (int) ge);
                Util.write16(r, 14, (int) (((ir + bo + ge + 9) / 10) & 0x3fff) | cls << 14);
                return r;
            }
            case "wormhole": {
                int num = Integer.parseInt(t[2]);
                int years = 0;
                Util.write16(r, 0, 2 << 13 | num);
                Util.write16(r, 2, Integer.parseInt(t[3]));
                Util.write16(r, 4, Integer.parseInt(t[4]));
                Util.write16(r, 12, 2 << 13 | Integer.parseInt(t[5]));
                int cls = Integer.parseInt(t[6]);
                for (i = 7; i < t.length; i++) {
                    switch (t[i]) {
                        case "years": years = Integer.parseInt(t[++i]); break;
                        case "seen": Util.write16(r, 8, Integer.decode(t[++i])); break;
                        case "seen2": Util.write16(r, 10, Integer.decode(t[++i])); break;
                        default: throw new Exception("wormhole: unknown token " + t[i]);
                    }
                }
                Util.write16(r, 6, (cls & 3) | (years & 0x3ff) << 2);
                return r;
            }
            case "trader": {
                int num = Integer.parseInt(t[2]);
                Util.write16(r, 0, 3 << 13 | num);
                for (int k = 0; k < 4; k++) Util.write16(r, 2 + 2 * k, Integer.parseInt(t[3 + k]));
                Util.write16(r, 10, Integer.parseInt(t[7]) & 15);
                for (i = 8; i < t.length; i++) {
                    switch (t[i]) {
                        case "met": Util.write16(r, 12, Integer.decode(t[++i])); break;
                        case "item": Util.write16(r, 14, Integer.decode(t[++i])); break;
                        default: throw new Exception("trader: unknown token " + t[i]);
                    }
                }
                return r;
            }
            default: throw new Exception("thing: unknown kind " + kind);
        }
    }

    // Turn messages (block 12). Each record: word w (id = w & 0x1ff, size flags =
    // w >> 9), word obj, then the message's parameters, parameter k being 2 bytes
    // when flag bit k is set and 1 byte otherwise. How many parameters each id takes
    // is read at run time from the local original game (STARS_EXE, default the
    // oracle run copy); without it only the raw line is printed.
    static byte[] msgParams;
    static final Map<Integer, String> MSG_NAMES = new HashMap<>();
    static {
        String[] n = {"c2", "mine-swept", "c3", "mine-laid", "c4", "mine-added", "c5", "mine-stopped",
            "c6", "mine-hit", "c7", "mine-hit-losses", "c8", "mine-annihilated", "c9", "own-mine-stopped",
            "ca", "own-mine-hit", "cb", "own-mine-hit-kills", "cc", "own-mine-annihilated",
            "be", "own-mine-swept", "bf", "lay-no-pod", "f4", "starbase-swept", "111", "target-field-gone",
            "15f", "detonate-annihilated", "160", "detonate-hit", "161", "detonate-hit-losses",
            "162", "own-detonate-annihilated", "163", "own-detonate-hit", "164", "own-detonate-hit-kills",
            "17e", "lay-failed"};
        for (int i = 0; i < n.length; i += 2) MSG_NAMES.put(Integer.parseInt(n[i], 16), n[i + 1]);
    }

    static byte[] msgParams() {
        if (msgParams != null) return msgParams.length == 0 ? null : msgParams;
        msgParams = new byte[0];
        String exe = System.getenv("STARS_EXE");
        if (exe == null) exe = System.getProperty("user.home")
            + "/.stars-oracle/run/StarsBox.app/Contents/Resources/c_drive/STARS/stars.exe";
        try {
            byte[] x = Files.readAllBytes(Paths.get(exe));
            byte[] sum = java.security.MessageDigest.getInstance("SHA-256").digest(x);
            if (String.format("%02x%02x%02x%02x", sum[0], sum[1], sum[2], sum[3]).equals("10f8b5f9"))
                msgParams = Arrays.copyOfRange(x, 0x1eca6, 0x1eca6 + 0x1c0);
        } catch (Exception e) {
            // no local game: raw only
        }
        return msgParams.length == 0 ? null : msgParams;
    }

    static void printMessages(String f, byte[] d, int size) {
        byte[] t = msgParams();
        if (t == null) return;
        int i = 0;
        while (i + 4 <= size) {
            int w = u16(d, i), id = w & 0x1ff, fl = w >> 9, obj = u16(d, i + 2);
            i += 4;
            if (id >= t.length) { System.out.printf("%s msg bad id=0x%x at=%d%n", f, id, i - 4); return; }
            StringBuilder p = new StringBuilder();
            for (int k = 0; k < (t[id] & 0xff); k++) {
                int v;
                if ((fl >> k & 1) != 0) { v = u16(d, i); i += 2; } else { v = d[i] & 0xff; i += 1; }
                p.append(k == 0 ? "" : ",").append(v);
            }
            System.out.printf("%s msg id=0x%x name=%s obj=0x%04x p=%s%n", f, id,
                MSG_NAMES.getOrDefault(id, "-"), obj, p);
        }
        if (i != size) System.out.printf("%s msg trailing=%d%n", f, size - i);
    }

    // Dump line for one object block (count or 18-byte record).
    static String thingString(byte[] d, int size) {
        if (size == 2) return "things count=" + u16(d, 0);
        StringBuilder h = new StringBuilder();
        for (int i = 0; i < size; i++) h.append(String.format("%02x", d[i]));
        int id = u16(d, 0), type = id >> 13, owner = (id >> 9) & 15, num = id & 0x1ff;
        String head = String.format("thing id=%d type=%s owner=%d num=%d x=%d y=%d", id,
            new String[]{"minefield", "packet", "wormhole", "trader"}[type], owner, num, u16(d, 2), u16(d, 4));
        String body;
        switch (type) {
            case 0: body = String.format(" count=%d known=%04x kind=%d det=%d seen=%04x w10=%04x",
                Util.read32(d, 6), u16(d, 10), d[12] & 0xff, d[13] & 0xff, u16(d, 14), u16(d, 16)); break;
            case 1: body = String.format(" dest=%d warp=%d moved=%d bit15=%d cargo=%d/%d/%d total10=%d class=%d w16=%04x",
                u16(d, 6) & 0x3ff, ((u16(d, 6) >> 10) & 15) + 4, (u16(d, 6) >> 14) & 1, u16(d, 6) >> 15,
                u16(d, 8), u16(d, 10), u16(d, 12), u16(d, 14) & 0x3fff, u16(d, 14) >> 14, u16(d, 16)); break;
            case 2: body = String.format(" class=%d years=%d seen=%04x seen2=%04x partner=%d w14=%04x w16=%04x",
                u16(d, 6) & 3, (u16(d, 6) >> 2) & 0x3ff, u16(d, 8), u16(d, 10), u16(d, 12) & 0x1ff, u16(d, 14), u16(d, 16)); break;
            default: body = String.format(" dest=%d,%d warp=%d w10=%04x met=%04x item=%04x w16=%04x",
                u16(d, 6), u16(d, 8), u16(d, 10) & 15, u16(d, 10), u16(d, 12), u16(d, 14), u16(d, 16)); break;
        }
        return head + body + " raw=" + h;
    }

    static FleetSpec parseFleet(String[] t) throws Exception {
        FleetSpec fs = new FleetSpec();
        fs.owner = Integer.parseInt(t[1]);
        fs.id = Integer.parseInt(t[2]);
        if (fs.id < 0 || fs.id > 511) throw new Exception("fleet id 0-511 expected, got " + fs.id);
        int i = 3;
        while (i < t.length) {
            switch (t[i]) {
                case "at": fs.x = Integer.parseInt(t[i + 1]); fs.y = Integer.parseInt(t[i + 2]); i += 3; break;
                case "ships":
                    for (String p : t[i + 1].split(",")) {
                        String[] dc = p.split(":");
                        fs.ships[Integer.parseInt(dc[0])] = Integer.parseInt(dc[1]);
                    }
                    i += 2; break;
                case "planet": fs.planet = Integer.parseInt(t[i + 1]); i += 2; break;
                case "target":
                    // target fleet OWNER ID: waypoint 0 targets that fleet (merge or transport with a fleet)
                    if (!t[i + 1].equals("fleet")) throw new Exception("target fleet OWNER ID");
                    fs.wp0Fleet = Integer.parseInt(t[i + 3]) | Integer.parseInt(t[i + 2]) << 9;
                    i += 4; break;
                case "plan": fs.plan = Integer.parseInt(t[i + 1]); i += 2; break;
                case "fuel": fs.fuel = Integer.parseInt(t[i + 1]); i += 2; break;
                case "dmg":
                    // dmg D:UNITS:PCT[,...]  damage word per design (UNITS/500 of armor, PCT% of ships)
                    for (String p : t[i + 1].split(",")) {
                        String[] du = p.split(":");
                        fs.dmg[Integer.parseInt(du[0])] = Integer.parseInt(du[1]) << 7 | Integer.parseInt(du[2]);
                    }
                    i += 2; break;
                case "cargo":
                    for (int k = 0; k < 4; k++) fs.cargo[k] = Long.parseLong(t[i + 1 + k]);
                    i += 5; break;
                case "task": {
                    int[] ord = new int[5];
                    int w = fs.wps.size();
                    fs.task.put(w, parseTask(t, i + 1, ord));
                    fs.orders.put(w, ord);
                    i += t[i + 1].equals("transport") || t[i + 1].equals("transfer")
                        || (t[i + 1].equals("lay") && i + 2 < t.length && t[i + 2].matches("\\d+")) ? 3 : 2;
                    break;
                }
                case "to": {
                    // to X Y [planet N] warp W
                    int x = Integer.parseInt(t[i + 1]), y = Integer.parseInt(t[i + 2]);
                    i += 3;
                    int obj = 0, type = 0x14;
                    if (t[i].equals("planet")) { obj = Integer.parseInt(t[i + 1]); type = 0x11; i += 2; }
                    else if (t[i].equals("thing")) { obj = Integer.decode(t[i + 1]); type = 0x18; i += 2; }
                    else if (t[i].equals("fleet")) {
                        obj = Integer.parseInt(t[i + 2]) | Integer.parseInt(t[i + 1]) << 9; type = 0x12; i += 3;
                    }
                    if (!t[i].equals("warp")) throw new Exception("to X Y [planet N|thing ID|fleet OWNER ID] warp W");
                    fs.wps.add(new int[]{x, y, obj, type, Integer.parseInt(t[i + 1])});
                    i += 2;
                    break;
                }
                default: throw new Exception("unknown fleet token " + t[i]);
            }
        }
        return fs;
    }
}
