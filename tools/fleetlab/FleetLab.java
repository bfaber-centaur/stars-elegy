import java.io.*;
import java.nio.file.*;
import java.util.*;

import org.starsautohost.starsapi.Util;
import org.starsautohost.starsapi.block.*;
import org.starsautohost.starsapi.encryption.Decryptor;

// FleetLab: build controlled fleet-movement starting states by editing a
// Stars! .HST with StarsAPI, and dump fleet state from .HST/.M files.
//
//   FleetLab dump FILE...
//   FleetLab build BASE.HST SPEC OUT.HST
//
// SPEC is line based ('#' starts a comment):
//   tech FIELD LEVEL                 set player 0 tech (energy weapons prop con elec bio)
//   design N clone M engine ITEM      add ship design N as a copy of design M with
//                                     every engine slot set to engine item id ITEM
//   fleet ID [planet P] at X Y ships D:C[,D:C...] fuel F [cargo IR BO GE COL]
//            {wp X Y WARP | wpp P X Y WARP | wpf F X Y WARP}...
// Every fleet of player 0 in BASE is replaced by the SPEC fleets. Waypoint 0
// is generated at the fleet's position; listed waypoints follow it.
public class FleetLab {
    static final String[] TECH = {"energy", "weapons", "prop", "con", "elec", "bio"};

    public static void main(String[] args) throws Exception {
        if (args.length >= 2 && args[0].equals("dump")) {
            for (int i = 1; i < args.length; i++) dump(args[i]);
        } else if (args.length == 4 && args[0].equals("build")) {
            build(args[1], args[2], args[3]);
        } else {
            System.err.println("usage: FleetLab dump FILE... | build BASE.HST SPEC OUT.HST");
            System.exit(2);
        }
    }

    static void dump(String f) throws Exception {
        List<Block> blocks = new Decryptor().readFile(f);
        int turn = -1;
        Map<Integer, DesignBlock> designs = new TreeMap<>();
        PartialFleetBlock cur = null;
        int wpIndex = 0;
        for (Block b : blocks) {
            if (b instanceof FileHeaderBlock) {
                FileHeaderBlock h = (FileHeaderBlock) b;
                turn = h.turn;
                System.out.printf("%s file turn=%d year=%d player=%d%n", f, h.turn, 2400 + h.turn, h.playerNumber);
            } else if (b instanceof PlayerBlock) {
                PlayerBlock p = (PlayerBlock) b;
                StringBuilder sb = new StringBuilder();
                if (p.fullDataBytes != null)
                    for (int i = 0; i < 6; i++) sb.append(' ').append(TECH[i]).append('=').append(p.fullDataBytes[0x12 + i]);
                System.out.printf("%s player %d designs=%d fleets=%d prt=%d lrt=%s%s%n", f, p.playerNumber,
                    p.shipDesignCount, p.fleets,
                    p.fullDataBytes == null ? -1 : p.fullDataBytes[0x44],
                    p.fullDataBytes == null ? "?" : String.format("%04x", ((p.fullDataBytes[0x47] & 0xff) << 8) | (p.fullDataBytes[0x46] & 0xff)),
                    sb);
            } else if (b instanceof DesignBlock) {
                DesignBlock d = (DesignBlock) b;
                if (d.isStarbase) continue;
                designs.put(d.designNumber, d);
                StringBuilder sb = new StringBuilder();
                for (DesignBlock.Slot s : d.slots)
                    if (s.count > 0) sb.append(String.format(" %x:%d*%d", s.category, s.itemId, s.count));
                System.out.printf("%s design %d hull=%d mass=%d fuelcap=%d full=%s slots=%s%n", f, d.designNumber,
                    d.hullId, d.mass, d.fuelCapacity, d.isFullDesign, sb);
            } else if (b instanceof PartialFleetBlock) {
                PartialFleetBlock fl = (PartialFleetBlock) b;
                cur = fl;
                wpIndex = 0;
                StringBuilder ships = new StringBuilder();
                long mass = 0;
                for (int i = 0; i < 16; i++) if (fl.shipCount[i] > 0) {
                    ships.append(ships.length() > 0 ? "," : "").append(i).append(':').append(fl.shipCount[i]);
                    if (designs.containsKey(i)) mass += (long) designs.get(i).mass * fl.shipCount[i];
                }
                mass += fl.ironium + fl.boranium + fl.germanium + fl.population;
                System.out.printf("%s fleet %d owner=%d kind=%d b2=%02x b3=%02x b5=%02x obj=%d x=%d y=%d ships=%s cargo=%d/%d/%d/%d fuel=%d mass=%d waypoints=%d%s%n",
                    f, fl.fleetNumber, fl.owner, fl.kindByte, fl.byte2 & 0xff, fl.byte3 & 0xff, fl.byte5 & 0xff,
                    fl.positionObjectId, fl.x, fl.y, ships, fl.ironium, fl.boranium, fl.germanium, fl.population,
                    fl.fuel, mass, fl.waypointCount,
                    fl.kindByte == PartialFleetBlock.FULL_KIND ? "" : String.format(" dx=%d dy=%d warp=%d mass=%d", fl.deltaX, fl.deltaY, fl.warp, fl.mass));
            } else if (b instanceof WaypointBlock) {
                WaypointBlock w = (WaypointBlock) b;
                StringBuilder extra = new StringBuilder();
                for (Byte x : w.additionalBytes) extra.append(String.format("%02x", x));
                System.out.printf("%s   wp fleet=%d i=%d x=%d y=%d obj=%d type=%02x warp=%d task=%d%s%n", f,
                    cur == null ? -1 : cur.fleetNumber, wpIndex++, w.x, w.y, w.positionObject, w.positionObjectType,
                    w.warp, w.waypointTask, extra.length() > 0 ? " extra=" + extra : "");
            } else if (b.typeId != BlockType.PLANET && b.typeId != BlockType.PARTIAL_PLANET
                       && b.typeId != BlockType.FILE_FOOTER && b.typeId != BlockType.PLANETS) {
                System.out.printf("%s block type=%d size=%d data=%s%n", f, b.typeId, b.size,
                    Util.bytesToString(b.getDecryptedData(), 0, b.size).trim());
            }
        }
    }

    static class FleetSpec {
        int id, planet = -1, x, y, fuel;
        long[] cargo = new long[4];
        int[] ships = new int[16];
        List<int[]> wps = new ArrayList<>(); // x, y, obj, type, warp
    }

    static void build(String base, String spec, String out) throws Exception {
        Decryptor dec = new Decryptor();
        List<Block> blocks = dec.readFile(base);
        Map<String, Integer> tech = new HashMap<>();
        List<int[]> clones = new ArrayList<>(); // n, m, engine
        List<FleetSpec> fleets = new ArrayList<>();
        int lineNo = 0;
        for (String raw : Files.readAllLines(Paths.get(spec))) {
            lineNo++;
            String line = raw.replaceAll("#.*", "").trim();
            if (line.isEmpty()) continue;
            String[] t = line.split("\\s+");
            try {
                if (t[0].equals("tech")) {
                    tech.put(t[1], Integer.parseInt(t[2]));
                } else if (t[0].equals("design")) {
                    if (!t[2].equals("clone") || !t[4].equals("engine")) throw new Exception("bad design line");
                    clones.add(new int[]{Integer.parseInt(t[1]), Integer.parseInt(t[3]), Integer.parseInt(t[5])});
                } else if (t[0].equals("fleet")) {
                    fleets.add(parseFleet(t));
                } else throw new Exception("unknown directive " + t[0]);
            } catch (Exception e) {
                throw new Exception(spec + ":" + lineNo + ": " + e.getMessage(), e);
            }
        }

        List<Block> outBlocks = new ArrayList<>();
        PlayerBlock player = null;
        int playerIndex = -1;
        int lastShipDesignIndex = -1;
        int firstFleetIndex = -1;
        Map<Integer, DesignBlock> designs = new TreeMap<>();
        boolean skippingFleet = false;
        for (Block b : blocks) {
            if (b instanceof PlayerBlock && ((PlayerBlock) b).playerNumber == 0) {
                player = (PlayerBlock) b;
                playerIndex = outBlocks.size();
            }
            if (b instanceof DesignBlock && !((DesignBlock) b).isStarbase) {
                designs.put(((DesignBlock) b).designNumber, (DesignBlock) b);
                lastShipDesignIndex = outBlocks.size();
            }
            if (b instanceof PartialFleetBlock) {
                PartialFleetBlock fl = (PartialFleetBlock) b;
                skippingFleet = fl.owner == 0;
                if (skippingFleet) {
                    if (firstFleetIndex < 0) firstFleetIndex = outBlocks.size();
                    continue;
                }
            } else if (b instanceof WaypointBlock) {
                if (skippingFleet) continue;
            } else {
                skippingFleet = false;
            }
            outBlocks.add(b);
        }
        if (player == null) throw new Exception("no player 0 block");
        if (firstFleetIndex < 0) throw new Exception("no player 0 fleet to use as a template");

        // Tech levels: patch player full data in place.
        byte[] pd = Arrays.copyOf(player.getDecryptedData(), player.size);
        for (Map.Entry<String, Integer> e : tech.entrySet()) {
            int i = Arrays.asList(TECH).indexOf(e.getKey());
            if (i < 0) throw new Exception("unknown tech field " + e.getKey());
            pd[8 + 0x12 + i] = (byte) (int) e.getValue();
        }

        // Designs.
        List<Block> newDesigns = new ArrayList<>();
        for (int[] c : clones) {
            DesignBlock src = designs.get(c[1]);
            if (src == null) throw new Exception("no design " + c[1]);
            if (designs.containsKey(c[0])) throw new Exception("design " + c[0] + " exists");
            byte[] d = Arrays.copyOf(src.getDecryptedData(), src.size);
            d[1] = (byte) ((d[1] & ~0x3c) | (c[0] << 2));
            int slotCount = d[6] & 0xff;
            boolean found = false;
            for (int s = 0; s < slotCount; s++) {
                int off = 17 + 4 * s;
                if (Util.read16(d, off) == 1) { d[off + 2] = (byte) c[2]; found = true; }
            }
            if (!found) throw new Exception("design " + c[1] + " has no engine slot");
            DesignBlock nd = new DesignBlock();
            nd.setDecryptedData(d, d.length);
            nd.decode();
            nd.setData(d, d.length);
            designs.put(c[0], nd);
            newDesigns.add(nd);
        }

        // Fleets.
        List<Block> newFleets = new ArrayList<>();
        Block template = null;
        for (Block b : blocks) if (b instanceof PartialFleetBlock && ((PartialFleetBlock) b).owner == 0) { template = b; break; }
        byte[] tpl = Arrays.copyOf(template.getDecryptedData(), template.size);
        fleets.sort(Comparator.comparingInt(f -> f.id));
        Set<Integer> ids = new HashSet<>();
        for (FleetSpec fs : fleets) {
            if (!ids.add(fs.id)) throw new Exception("duplicate fleet " + fs.id);
            FleetBlock fl = new FleetBlock();
            fl.setDecryptedData(tpl, tpl.length);
            fl.decode();
            fl.fleetNumber = fs.id;
            fl.owner = 0;
            fl.positionObjectId = fs.planet >= 0 ? fs.planet : 0xFFFF;
            fl.x = fs.x;
            fl.y = fs.y;
            fl.shipTypes = 0;
            boolean big = false;
            for (int i = 0; i < 16; i++) {
                fl.shipCount[i] = fs.ships[i];
                if (fs.ships[i] > 0) {
                    if (!designs.containsKey(i)) throw new Exception("fleet " + fs.id + ": no design " + i);
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
            fl.battlePlan = 0;
            fl.waypointCount = 1 + fs.wps.size();
            fl.encode();
            fl.setData(fl.getDecryptedData(), fl.size);
            newFleets.add(fl);
            List<int[]> all = new ArrayList<>();
            all.add(fs.planet >= 0 ? new int[]{fs.x, fs.y, fs.planet, 0x11, 0} : new int[]{fs.x, fs.y, 0, 0x14, 0});
            all.addAll(fs.wps);
            for (int[] w : all) {
                WaypointBlock wb = new WaypointBlock();
                wb.x = w[0]; wb.y = w[1]; wb.positionObject = w[2]; wb.positionObjectType = w[3];
                wb.warp = w[4]; wb.waypointTask = 0;
                wb.encode();
                newFleets.add(wb);
            }
        }

        // Splice: new designs after the last ship design, fleets where the
        // first player-0 fleet was.
        List<Block> result = new ArrayList<>();
        for (int i = 0; i < outBlocks.size(); i++) {
            if (i == firstFleetIndex) result.addAll(newFleets);
            result.add(outBlocks.get(i));
            if (i == lastShipDesignIndex) result.addAll(newDesigns);
        }
        if (firstFleetIndex == outBlocks.size()) result.addAll(newFleets);

        int designCount = 0;
        for (int k : designs.keySet()) designCount = Math.max(designCount, k + 1);
        pd[1] = (byte) designs.size();
        pd[4] = (byte) (fleets.size() & 0xff);
        pd[5] = (byte) ((pd[5] & 0xf0) | (fleets.size() >> 8));
        player.setDecryptedData(pd, pd.length);
        player.decode();
        player.setData(pd, pd.length);

        dec.writeBlocks(out, result, false);
        System.out.printf("wrote %s: %d designs, %d fleets%n", out, designs.size(), fleets.size());
    }

    static FleetSpec parseFleet(String[] t) throws Exception {
        FleetSpec fs = new FleetSpec();
        fs.id = Integer.parseInt(t[1]);
        int i = 2;
        while (i < t.length) {
            switch (t[i]) {
                case "planet": fs.planet = Integer.parseInt(t[i + 1]); i += 2; break;
                case "at": fs.x = Integer.parseInt(t[i + 1]); fs.y = Integer.parseInt(t[i + 2]); i += 3; break;
                case "ships":
                    for (String p : t[i + 1].split(",")) {
                        String[] dc = p.split(":");
                        fs.ships[Integer.parseInt(dc[0])] = Integer.parseInt(dc[1]);
                    }
                    i += 2; break;
                case "fuel": fs.fuel = Integer.parseInt(t[i + 1]); i += 2; break;
                case "cargo":
                    for (int k = 0; k < 4; k++) fs.cargo[k] = Long.parseLong(t[i + 1 + k]);
                    i += 5; break;
                case "wp":
                    fs.wps.add(new int[]{Integer.parseInt(t[i + 1]), Integer.parseInt(t[i + 2]), 0, 0x14, Integer.parseInt(t[i + 3])});
                    i += 4; break;
                case "wpp":
                    fs.wps.add(new int[]{Integer.parseInt(t[i + 2]), Integer.parseInt(t[i + 3]), Integer.parseInt(t[i + 1]), 0x11, Integer.parseInt(t[i + 4])});
                    i += 5; break;
                case "wpf":
                    fs.wps.add(new int[]{Integer.parseInt(t[i + 2]), Integer.parseInt(t[i + 3]), Integer.parseInt(t[i + 1]), 0x12, Integer.parseInt(t[i + 4])});
                    i += 5; break;
                default: throw new Exception("unknown fleet token " + t[i]);
            }
        }
        return fs;
    }
}
