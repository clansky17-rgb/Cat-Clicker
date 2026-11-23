import pygame
import sys
import os
import json
import math
import array
import socket
import threading
import copy

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
clock = pygame.time.Clock()

info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
windowed_size = (min(WIDTH, 1000), min(HEIGHT, 700))

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
except pygame.error:
    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)

pygame.display.set_caption("Clicker Cat")
pygame.mouse.set_visible(False)
is_fullscreen = bool(screen.get_flags() & pygame.FULLSCREEN)


def toggle_fullscreen():
    global screen, is_fullscreen, windowed_size
    if is_fullscreen:
        screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
        is_fullscreen = False
    else:
        windowed_size = screen.get_size()
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        is_fullscreen = True

BG = (255, 245, 228)
SHOP_BG = (250, 234, 210)
CARD_AFFORD = (255, 255, 255)
CARD_LOCKED = (232, 220, 205)
CARD_OWNED = (255, 243, 196)
ORANGE = (244, 162, 97)
DARK_ORANGE = (217, 119, 54)
INNER_EAR = (255, 183, 197)
OUTLINE = (74, 53, 37)
EYE = (43, 45, 66)
BLUSH = (255, 153, 172)
NOSE = (255, 117, 143)
WHITE = (255, 255, 255)
FISH_BLUE = (72, 180, 224)
FISH_FIN = (130, 210, 240)
P2_PINK = (235, 110, 165)
P2_FIN = (255, 175, 205)
GREEN = (64, 145, 108)
GOLD_TEXT = (184, 134, 11)
RED_BTN = (224, 102, 102)
WARN_BTN = (244, 162, 97)
BLUE_BTN = (72, 149, 239)


def make_tone(freq_start, freq_end, duration, volume=0.25):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array("h")
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        env = (1.0 - progress) ** 1.5
        val = int(32767 * volume * env * math.sin(2 * math.pi * freq * t))
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


try:
    click_sound = make_tone(420, 680, 0.08, 0.22)
    buy_sound = make_tone(520, 880, 0.16, 0.28)
    has_audio = True
except pygame.error:
    has_audio = False

sound_enabled = True


def play_sfx(snd):
    if has_audio and sound_enabled:
        snd.play()
def build_cat_head(fur_col, stripe_col, ear_in, eye_col=EYE, white_muzzle=False):
    surf = pygame.Surface((210, 150), pygame.SRCALPHA)
    pygame.draw.polygon(surf, fur_col, [(40, 55), (25, 5), (80, 35)])
    pygame.draw.polygon(surf, OUTLINE, [(40, 55), (25, 5), (80, 35)], 4)
    pygame.draw.polygon(surf, fur_col, [(170, 55), (185, 5), (130, 35)])
    pygame.draw.polygon(surf, OUTLINE, [(170, 55), (185, 5), (130, 35)], 4)
    pygame.draw.polygon(surf, ear_in, [(44, 48), (33, 16), (68, 36)])
    pygame.draw.polygon(surf, ear_in, [(166, 48), (177, 16), (142, 36)])
    pygame.draw.ellipse(surf, fur_col, (30, 25, 150, 115))
    if white_muzzle:
        pygame.draw.ellipse(surf, (248, 248, 250), (62, 82, 86, 54))
    pygame.draw.ellipse(surf, OUTLINE, (30, 25, 150, 115), 4)
    if stripe_col:
        for x in (90, 105, 120):
            pygame.draw.line(surf, stripe_col, (x, 28), (x, 45), 4)
    for x in (70, 140):
        pygame.draw.ellipse(surf, eye_col, (x - 11, 68, 22, 26))
        pygame.draw.circle(surf, WHITE, (x - 4, 76), 4)
    pygame.draw.ellipse(surf, BLUSH, (43, 92, 22, 13))
    pygame.draw.ellipse(surf, BLUSH, (145, 92, 22, 13))
    mouth_col = (190, 180, 175) if fur_col == (34, 34, 40) else OUTLINE
    pygame.draw.ellipse(surf, NOSE, (99, 88, 12, 8))
    pygame.draw.arc(surf, mouth_col, (87, 90, 18, 16), 3.14, 6.28, 3)
    pygame.draw.arc(surf, mouth_col, (105, 90, 18, 16), 3.14, 6.28, 3)
    pygame.draw.line(surf, OUTLINE, (36, 84), (6, 78), 3)
    pygame.draw.line(surf, OUTLINE, (36, 94), (6, 98), 3)
    pygame.draw.line(surf, OUTLINE, (174, 84), (204, 78), 3)
    pygame.draw.line(surf, OUTLINE, (174, 94), (204, 98), 3)
    return surf


def build_fish_cursor(body_col, fin_col):
    surf = pygame.Surface((48, 32), pygame.SRCALPHA)
    pygame.draw.polygon(surf, fin_col, [(32, 16), (46, 5), (46, 27)])
    pygame.draw.polygon(surf, OUTLINE, [(32, 16), (46, 5), (46, 27)], 2)
    pygame.draw.polygon(surf, fin_col, [(16, 7), (24, 1), (27, 8)])
    pygame.draw.polygon(surf, OUTLINE, [(16, 7), (24, 1), (27, 8)], 2)
    pygame.draw.ellipse(surf, body_col, (2, 6, 34, 20))
    pygame.draw.ellipse(surf, OUTLINE, (2, 6, 34, 20), 2)
    pygame.draw.circle(surf, WHITE, (10, 14), 4)
    pygame.draw.circle(surf, EYE, (9, 14), 2)
    return surf


cat_classic = build_cat_head(ORANGE, DARK_ORANGE, INNER_EAR)
cat_tl = build_cat_head((78, 82, 88), (45, 48, 52), INNER_EAR, white_muzzle=True)
cat_tr = build_cat_head((168, 136, 104), (112, 85, 60), INNER_EAR)
cat_bl = build_cat_head((155, 158, 164), (105, 108, 114), INNER_EAR)
cat_br = build_cat_head((34, 34, 40), None, (85, 65, 75), eye_col=(245, 208, 70))

cat_squad = pygame.Surface((210, 150), pygame.SRCALPHA)
cat_squad.blit(cat_tl, (0, 0), (0, 0, 105, 82))
cat_squad.blit(cat_tr, (105, 0), (105, 0, 105, 82))
cat_squad.blit(cat_bl, (0, 82), (0, 82, 105, 68))
cat_squad.blit(cat_br, (105, 82), (105, 82, 105, 68))
pygame.draw.line(cat_squad, WHITE, (105, 18), (105, 140), 2)
pygame.draw.line(cat_squad, WHITE, (30, 82), (180, 82), 2)

SCALE = 2.4
base_w = int(210 * SCALE)
base_h = int(150 * SCALE)

SKIN_NAMES = ("Classic Orange", "4-Cat Squad!", "Violet", "Biscuit", "Bean", "Void")
SKIN_SURFS = {
    "Classic Orange": pygame.transform.smoothscale(cat_classic, (base_w, base_h)),
    "4-Cat Squad!": pygame.transform.smoothscale(cat_squad, (base_w, base_h)),
    "Violet": pygame.transform.smoothscale(cat_tl, (base_w, base_h)),
    "Biscuit": pygame.transform.smoothscale(cat_tr, (base_w, base_h)),
    "Bean": pygame.transform.smoothscale(cat_bl, (base_w, base_h)),
    "Void": pygame.transform.smoothscale(cat_br, (base_w, base_h)),
}
current_skin_idx = 0
big_cat = SKIN_SURFS.get("Classic Orange")
squish = 0.0

fish_cursor = build_fish_cursor(FISH_BLUE, FISH_FIN)
p2_cursor = build_fish_cursor(P2_PINK, P2_FIN)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HIGH_SCORE_FILE = os.path.join(SCRIPT_DIR, "high score.txt")
SAVE_FILE = os.path.join(SCRIPT_DIR, "save_data.json")
UNLOCK_FILE = os.path.join(SCRIPT_DIR, "special_skins_unlocked.txt")

DEFAULT_SHOP = [
    {"name": "Feather Toy", "desc": "+1 per click", "cost": 15, "owned": 0, "max": None, "type": "click", "power": 1},
    {"name": "Auto-Petter", "desc": "+1 per sec", "cost": 50, "owned": 0, "max": None, "type": "auto", "power": 1},
    {"name": "Laser Pointer", "desc": "+5 per click", "cost": 120, "owned": 0, "max": None, "type": "click", "power": 5},
    {"name": "Catnip Farm", "desc": "+8 per sec", "cost": 300, "owned": 0, "max": None, "type": "auto", "power": 8},
    {"name": "Tuna Buffet", "desc": "+25 per click", "cost": 900, "owned": 0, "max": None, "type": "click", "power": 25},
    {"name": "Cat Cafe Empire", "desc": "+50 per sec", "cost": 2500, "owned": 0, "max": None, "type": "auto", "power": 50},
    {"name": "Violet", "desc": "+250 per click (Unique)", "cost": 10000, "owned": 0, "max": 1, "type": "click", "power": 250},
    {"name": "Biscuit", "desc": "+500 per sec (Unique)", "cost": 50000, "owned": 0, "max": 1, "type": "auto", "power": 500},
    {"name": "Void", "desc": "+2,500 per click (Unique)", "cost": 250000, "owned": 0, "max": 1, "type": "click", "power": 2500},
    {"name": "Bean", "desc": "+10,000 per sec (Unique)", "cost": 1000000, "owned": 0, "max": 1, "type": "auto", "power": 10000},
]


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip, _ = s.getsockname()
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


NET_PORT = 5555
net_role = "offline"
net_conn = None
net_server = None
net_connected = False
net_lock = threading.Lock()

ui_screen = "game"
battle_phase = "solo"
battle_duration = 30
battle_timer = 0.0
p1_final_score = 0
p2_final_score = 0
partner_x = 0.5
partner_y = 0.5

typing_mode = None
ip_input = ""
custom_time_input = ""


def reset_run_stats():
    global clicks, per_click, per_sec, shop_items, shop_scroll, floating_texts
    clicks = 0.0
    per_click = 1
    per_sec = 0
    shop_items = copy.deepcopy(DEFAULT_SHOP)
    shop_scroll = 0
    floating_texts = []


def net_send(msg_dict):
    global net_connected
    if net_conn and net_connected:
        try:
            data = (json.dumps(msg_dict) + "\n").encode("utf-8")
            net_conn.sendall(data)
        except Exception:
            net_connected = False


def close_network():
    global net_role, net_conn, net_server, net_connected, battle_phase
    net_connected = False
    net_role = "offline"
    battle_phase = "solo"
    for sock in (net_conn, net_server):
        if sock:
            try:
                sock.close()
            except Exception:
                pass
    net_conn = None
    net_server = None


def is_my_turn():
    if battle_phase == "solo":
        return True
    if battle_phase == "p1_turn" and net_role == "host":
        return True
    if battle_phase == "p2_turn" and net_role == "client":
        return True
    return False
def net_receive_loop(conn):
    global clicks, per_click, per_sec, shop_items, partner_x, partner_y, squish
    global net_connected, battle_phase, battle_duration, battle_timer
    global p1_final_score, p2_final_score, ui_screen, floating_texts
    buf = ""
    while net_connected:
        try:
            chunk = conn.recv(4096).decode("utf-8")
            if not chunk:
                break
            buf += chunk
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                if not line.strip():
                    continue
                msg = json.loads(line)
                with net_lock:
                    mtype = msg.get("type")
                    if mtype == "duration":
                        battle_duration = int(msg.get("sec", 30))
                    elif mtype == "start_p1":
                        battle_duration = int(msg.get("sec", 30))
                        battle_timer = float(battle_duration)
                        p1_final_score = 0
                        p2_final_score = 0
                        reset_run_stats()
                        battle_phase = "p1_turn"
                        ui_screen = "game"
                    elif mtype == "start_p2":
                        p1_final_score = int(msg.get("p1_score", 0))
                        battle_timer = float(battle_duration)
                        reset_run_stats()
                        battle_phase = "p2_turn"
                    elif mtype == "results":
                        p1_final_score = int(msg.get("p1_score", p1_final_score))
                        p2_final_score = int(msg.get("p2_score", 0))
                        battle_phase = "results"
                    elif mtype == "back_lobby":
                        battle_phase = "lobby"
                        ui_screen = "lobby"
                    elif mtype == "watch_click":
                        squish = 1.0
                        amt = msg.get("amount", 1)
                        nx = msg.get("nx", 0.35)
                        ny = msg.get("ny", 0.5)
                        floating_texts.append({
                            "text": f"+{amt:,}",
                            "x": float(nx * screen.get_width()),
                            "y": float(ny * screen.get_height() - 10),
                            "alpha": 255.0,
                        })
                    elif mtype == "watch_state":
                        clicks = float(msg.get("clicks", clicks))
                        per_click = int(msg.get("per_click", per_click))
                        per_sec = int(msg.get("per_sec", per_sec))
                        battle_timer = float(msg.get("timer", battle_timer))
                        items = msg.get("shop_items", [])
                        if len(items) == len(shop_items):
                            shop_items = items
                    elif mtype == "cursor":
                        partner_x = float(msg.get("nx", 0.5))
                        partner_y = float(msg.get("ny", 0.5))
        except Exception:
            break
    net_connected = False


def start_host():
    global net_role, net_server, net_conn, net_connected, battle_phase, status_msg, status_timer
    close_network()
    try:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(("0.0.0.0", NET_PORT))
        srv.listen(1)
        net_server = srv
        net_role = "host"
        battle_phase = "lobby"
        status_msg = "Lobby created! Waiting for Player 2..."
        status_timer = 10.0

        def accept_worker():
            global net_conn, net_connected, status_msg, status_timer
            try:
                conn, _ = srv.accept()
                net_conn = conn
                net_connected = True
                status_msg = "Player 2 Joined! Ready to Start!"
                status_timer = 4.0
                net_send({"type": "duration", "sec": battle_duration})
                net_receive_loop(conn)
            except Exception:
                pass

        threading.Thread(target=accept_worker, daemon=True).start()
    except Exception as e:
        status_msg = f"Host failed: {e}"
        status_timer = 3.0


def join_host(target_ip):
    global net_role, net_conn, net_connected, battle_phase, status_msg, status_timer
    close_network()
    try:
        cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cli.settimeout(4.0)
        cli.connect((target_ip.strip(), NET_PORT))
        cli.settimeout(None)
        net_conn = cli
        net_role = "client"
        net_connected = True
        battle_phase = "lobby"
        status_msg = "Joined Lobby! Waiting for Host to start..."
        status_timer = 5.0
        threading.Thread(target=net_receive_loop, args=(cli,), daemon=True).start()
    except Exception:
        close_network()
        status_msg = "Could not connect! Check IP & Wi-Fi."
        status_timer = 3.0
def load_high_score():
    if not os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "w") as f:
            f.write("0")
        return 0
    try:
        with open(HIGH_SCORE_FILE, "r") as f:
            return int(f.read().strip())
    except ValueError:
        return 0


def save_high_score():
    with open(HIGH_SCORE_FILE, "w") as f:
        f.write(str(high_score))


skins_unlocked = False


def read_skin_unlock():
    if not os.path.exists(UNLOCK_FILE):
        # Keep an unlock from an existing save when adding this flag for the first time.
        was_already_unlocked = False
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    was_already_unlocked = bool(json.load(f).get("skins_unlocked", False))
            except Exception:
                pass
        with open(UNLOCK_FILE, "w", encoding="utf-8") as f:
            f.write("1" if was_already_unlocked else "0")
        return was_already_unlocked
    try:
        with open(UNLOCK_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() == "1"
    except OSError:
        return False


def write_skin_unlock(unlocked):
    with open(UNLOCK_FILE, "w", encoding="utf-8") as f:
        f.write("1" if unlocked else "0")


def get_skin_by_idx(idx):
    target = idx % len(SKIN_NAMES)
    for i, name in enumerate(SKIN_NAMES):
        if i == target:
            return name
    return "Classic Orange"


def save_full_progress():
    save_high_score()
    data = {
        "clicks": clicks,
        "per_click": per_click,
        "per_sec": per_sec,
        "shop_items": shop_items,
        "skin_idx": current_skin_idx,
        "skins_unlocked": read_skin_unlock(),
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_full_progress():
    global clicks, per_click, per_sec, shop_items, current_skin_idx, big_cat, skins_unlocked
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        clicks = float(data.get("clicks", 0.0))
        per_click = int(data.get("per_click", 1))
        per_sec = int(data.get("per_sec", 0))
        saved_items = data.get("shop_items", [])
        if len(saved_items) == len(shop_items):
            shop_items = saved_items
        if read_skin_unlock():
            skins_unlocked = True
            current_skin_idx = int(data.get("skin_idx", 1)) % len(SKIN_NAMES)
            big_cat = SKIN_SURFS.get(get_skin_by_idx(current_skin_idx))
        else:
            skins_unlocked = False
            current_skin_idx = 0
            big_cat = SKIN_SURFS.get("Classic Orange")
        return True
    except Exception:
        return False


def quit_game():
    close_network()
    save_high_score()
    pygame.quit()
    sys.exit()


clicks = 0.0
high_score = load_high_score()
show_high_score = True
per_click = 1
per_sec = 0
shop_scroll = 0
shop_items = copy.deepcopy(DEFAULT_SHOP)


def count_unique_cats():
    names = {"Violet", "Biscuit", "Void", "Bean"}
    return sum(1 for item in shop_items if item["name"] in names and item["owned"] >= 1)


def load_permanent_unlocks():
    global skins_unlocked, current_skin_idx, big_cat
    file_unlocked = read_skin_unlock()
    skins_unlocked = file_unlocked
    current_skin_idx = 0
    big_cat = SKIN_SURFS.get("Classic Orange")
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            if file_unlocked:
                current_skin_idx = int(data.get("skin_idx", 1)) % len(SKIN_NAMES)
                big_cat = SKIN_SURFS.get(get_skin_by_idx(current_skin_idx))
        except Exception:
            pass


def all_four_unlocked():
    global skins_unlocked
    skins_unlocked = read_skin_unlock()
    return skins_unlocked


load_permanent_unlocks()

floating_texts = []
status_msg = ""
status_timer = 0.0
sync_timer = 0.0
mouse_held = False

font_big = pygame.font.SysFont("Arial", 44, bold=True)
font_med = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 20, bold=True)
font_float = pygame.font.SysFont("Arial", 34, bold=True)
while True:
    dt = clock.tick(60) / 1000.0
    scr_w, scr_h = screen.get_width(), screen.get_height()
    shop_w = 350
    play_center_x = (scr_w - shop_w) // 2

    if status_timer > 0:
        status_timer = max(0.0, status_timer - dt)
        if status_timer == 0:
            status_msg = ""

    with net_lock:
        if ui_screen == "game" and is_my_turn():
            clicks += per_sec * dt
            if int(clicks) > high_score:
                high_score = int(clicks)

            if battle_phase in ("p1_turn", "p2_turn"):
                battle_timer = max(0.0, battle_timer - dt)
                if battle_timer <= 0.0:
                    if battle_phase == "p1_turn" and net_role == "host":
                        p1_final_score = int(clicks)
                        battle_timer = float(battle_duration)
                        reset_run_stats()
                        battle_phase = "p2_turn"
                        net_send({"type": "start_p2", "p1_score": p1_final_score})
                    elif battle_phase == "p2_turn" and net_role == "client":
                        p2_final_score = int(clicks)
                        battle_phase = "results"
                        net_send({"type": "results", "p1_score": p1_final_score, "p2_score": p2_final_score})

    if net_connected:
        sync_timer += dt
        if sync_timer >= 0.06:
            sync_timer = 0.0
            mx_s, my_s = pygame.mouse.get_pos()
            net_send({"type": "cursor", "nx": mx_s / max(1, scr_w), "ny": my_s / max(1, scr_h)})
            if is_my_turn() and battle_phase in ("p1_turn", "p2_turn"):
                net_send({
                    "type": "watch_state",
                    "clicks": clicks,
                    "per_click": per_click,
                    "per_sec": per_sec,
                    "timer": battle_timer,
                    "shop_items": shop_items,
                })

    cat_rect = big_cat.get_rect(center=(play_center_x, scr_h // 2))

    card_h = 108
    card_gap = 16
    total_shop_h = len(shop_items) * (card_h + card_gap)
    max_scroll = max(0, total_shop_h - (scr_h - 125))
    shop_scroll = max(0, min(shop_scroll, max_scroll))

    shop_rects = []
    for i in range(len(shop_items)):
        cy = 105 + i * (card_h + card_gap) - shop_scroll
        card_rect = pygame.Rect(scr_w - shop_w + 20, cy, shop_w - 40, card_h)
        shop_rects.append(card_rect)

    opt_w, opt_h = 460, 680
    opt_rect = pygame.Rect((scr_w - opt_w) // 2, (scr_h - opt_h) // 2, opt_w, opt_h)
    bw, bh = 380, 44
    bx = opt_rect.centerx - bw // 2
    btn_resume = pygame.Rect(bx, opt_rect.y + 84, bw, bh)
    btn_open_lobby = pygame.Rect(bx, opt_rect.y + 138, bw, bh)
    btn_skin = pygame.Rect(bx, opt_rect.y + 192, bw, bh)
    btn_sound = pygame.Rect(bx, opt_rect.y + 246, bw, bh)
    btn_toggle_hs = pygame.Rect(bx, opt_rect.y + 300, bw, bh)
    btn_reset_hs = pygame.Rect(bx, opt_rect.y + 354, bw, bh)
    btn_save = pygame.Rect(bx, opt_rect.y + 408, bw, bh)
    btn_load = pygame.Rect(bx, opt_rect.y + 462, bw, bh)
    btn_fullscreen = pygame.Rect(bx, opt_rect.y + 516, bw, bh)
    btn_exit = pygame.Rect(bx, opt_rect.y + 570, bw, bh)
    lob_w, lob_h = 540, 560
    lob_rect = pygame.Rect((scr_w - lob_w) // 2, (scr_h - lob_h) // 2, lob_w, lob_h)
    lbw, lbh = 440, 48
    lbx = lob_rect.centerx - lbw // 2
    btn_create_lob = pygame.Rect(lbx, lob_rect.y + 130, lbw, lbh)
    btn_join_lob = pygame.Rect(lbx, lob_rect.y + 190, lbw, lbh)
    btn_preset_time = pygame.Rect(lbx, lob_rect.y + 250, 212, lbh)
    btn_custom_time = pygame.Rect(lbx + 228, lob_rect.y + 250, 212, lbh)
    btn_start_battle = pygame.Rect(lbx, lob_rect.y + 320, lbw, 54)
    btn_back_solo = pygame.Rect(lbx, lob_rect.y + 390, lbw, lbh)

    res_w, res_h = 500, 400
    res_rect = pygame.Rect((scr_w - res_w) // 2, (scr_h - res_h) // 2, res_w, res_h)
    btn_rematch = pygame.Rect(res_rect.centerx - 190, res_rect.y + 240, 380, 50)
    btn_res_lobby = pygame.Rect(res_rect.centerx - 190, res_rect.y + 305, 380, 50)

    if not any(pygame.mouse.get_pressed()):
        mouse_held = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit_game()

        if event.type == pygame.KEYDOWN:
            if typing_mode == "ip":
                if event.key == pygame.K_RETURN:
                    typing_mode = None
                    if ip_input.strip():
                        join_host(ip_input)
                elif event.key == pygame.K_ESCAPE:
                    typing_mode = None
                elif event.key == pygame.K_BACKSPACE:
                    ip_input = ip_input[:-1]
                elif event.unicode in "0123456789.":
                    ip_input += event.unicode
            elif typing_mode == "custom_time":
                if event.key == pygame.K_RETURN:
                    typing_mode = None
                    if custom_time_input.isdigit() and int(custom_time_input) >= 5:
                        battle_duration = int(custom_time_input)
                        net_send({"type": "duration", "sec": battle_duration})
                        status_msg = f"Custom time set to {battle_duration}s!"
                        status_timer = 2.5
                elif event.key == pygame.K_ESCAPE:
                    typing_mode = None
                elif event.key == pygame.K_BACKSPACE:
                    custom_time_input = custom_time_input[:-1]
                elif event.unicode.isdigit() and len(custom_time_input) < 4:
                    custom_time_input += event.unicode
            elif event.key == pygame.K_ESCAPE:
                if ui_screen == "lobby":
                    ui_screen = "options"
                elif ui_screen == "options":
                    ui_screen = "game"
                else:
                    ui_screen = "options"
                status_msg = ""

        if event.type == pygame.MOUSEWHEEL and ui_screen == "game":
            mx_now, _ = pygame.mouse.get_pos()
            if mx_now >= scr_w - shop_w:
                shop_scroll -= event.y * 35
                shop_scroll = max(0, min(shop_scroll, max_scroll))
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not mouse_held:
            mouse_held = True
            mx_c, my_c = event.pos
            if ui_screen == "options":
                if btn_resume.collidepoint(event.pos):
                    ui_screen = "game"
                elif btn_open_lobby.collidepoint(event.pos):
                    ui_screen = "lobby"
                    typing_mode = None
                elif btn_skin.collidepoint(event.pos):
                    if all_four_unlocked():
                        current_skin_idx = (current_skin_idx + 1) % len(SKIN_NAMES)
                        big_cat = SKIN_SURFS.get(get_skin_by_idx(current_skin_idx))
                        play_sfx(buy_sound)
                    else:
                        status_msg = f"Buy all 4 cats to unlock ({count_unique_cats()}/4)!"
                        status_timer = 2.5
                        play_sfx(click_sound)
                elif btn_sound.collidepoint(event.pos):
                    sound_enabled = not sound_enabled
                    play_sfx(click_sound)
                elif btn_toggle_hs.collidepoint(event.pos):
                    show_high_score = not show_high_score
                    play_sfx(click_sound)
                elif btn_reset_hs.collidepoint(event.pos):
                    high_score = 0
                    save_high_score()
                    status_msg = "High Score Reset to 0!"
                    status_timer = 2.0
                    play_sfx(click_sound)
                elif btn_save.collidepoint(event.pos):
                    save_full_progress()
                    status_msg = "Progress Saved!"
                    status_timer = 2.0
                    play_sfx(buy_sound)
                elif btn_load.collidepoint(event.pos):
                    if load_full_progress():
                        status_msg = "Save Loaded!"
                        play_sfx(buy_sound)
                    else:
                        status_msg = "No Save File Found!"
                    status_timer = 2.0
                elif btn_fullscreen.collidepoint(event.pos):
                    toggle_fullscreen()
                    play_sfx(click_sound)
                elif btn_exit.collidepoint(event.pos):
                    quit_game()

            elif ui_screen == "lobby":
                if btn_create_lob.collidepoint(event.pos):
                    typing_mode = None
                    if net_role == "host":
                        close_network()
                        status_msg = "Lobby closed."
                        status_timer = 2.0
                    else:
                        start_host()
                elif btn_join_lob.collidepoint(event.pos):
                    if net_role == "client":
                        close_network()
                        status_msg = "Left lobby."
                        status_timer = 2.0
                    else:
                        typing_mode = "ip"
                        ip_input = ""
                        status_msg = "Type Host IP & press ENTER"
                        status_timer = 20.0
                elif btn_preset_time.collidepoint(event.pos) and net_role != "client":
                    typing_mode = None
                    if battle_duration == 15:
                        battle_duration = 30
                    elif battle_duration == 30:
                        battle_duration = 60
                    elif battle_duration == 60:
                        battle_duration = 90
                    else:
                        battle_duration = 15
                    net_send({"type": "duration", "sec": battle_duration})
                    play_sfx(click_sound)
                elif btn_custom_time.collidepoint(event.pos) and net_role != "client":
                    typing_mode = "custom_time"
                    custom_time_input = ""
                    status_msg = "Type seconds (min 5) & press ENTER"
                    status_timer = 15.0
                elif btn_start_battle.collidepoint(event.pos) and net_role == "host" and net_connected:
                    with net_lock:
                        p1_final_score = 0
                        p2_final_score = 0
                        battle_timer = float(battle_duration)
                        reset_run_stats()
                        battle_phase = "p1_turn"
                        ui_screen = "game"
                    net_send({"type": "start_p1", "sec": battle_duration})
                    play_sfx(buy_sound)
                elif btn_back_solo.collidepoint(event.pos):
                    typing_mode = None
                    if battle_phase == "solo":
                        ui_screen = "game"
                    else:
                        close_network()
                        reset_run_stats()
                        ui_screen = "game"
            elif ui_screen == "game":
                if battle_phase == "results":
                    if btn_rematch.collidepoint(event.pos) and net_role == "host" and net_connected:
                        with net_lock:
                            p1_final_score = 0
                            p2_final_score = 0
                            battle_timer = float(battle_duration)
                            reset_run_stats()
                            battle_phase = "p1_turn"
                        net_send({"type": "start_p1", "sec": battle_duration})
                    elif btn_res_lobby.collidepoint(event.pos):
                        if net_connected:
                            battle_phase = "lobby"
                            ui_screen = "lobby"
                            net_send({"type": "back_lobby"})
                        else:
                            close_network()
                            reset_run_stats()
                elif is_my_turn():
                    if cat_rect.collidepoint(event.pos):
                        with net_lock:
                            squish = 1.0
                            clicks += per_click
                            if int(clicks) > high_score:
                                high_score = int(clicks)
                        play_sfx(click_sound)
                        floating_texts.append({
                            "text": f"+{per_click:,}",
                            "x": float(mx_c),
                            "y": float(my_c - 10),
                            "alpha": 255.0,
                        })
                        if battle_phase in ("p1_turn", "p2_turn"):
                            net_send({
                                "type": "watch_click",
                                "amount": per_click,
                                "nx": mx_c / max(1, scr_w),
                                "ny": my_c / max(1, scr_h),
                            })

                    if mx_c >= scr_w - shop_w and my_c >= 95:
                        for i, card_rect in enumerate(shop_rects):
                            item = shop_items[i]
                            maxed_out = item["max"] is not None and item["owned"] >= item["max"]
                            if card_rect.collidepoint(event.pos) and not maxed_out and clicks >= item["cost"]:
                                with net_lock:
                                    was_unlocked = all_four_unlocked()
                                    clicks -= item["cost"]
                                    item["owned"] += 1
                                    if item["max"] is None:
                                        item["cost"] = int(item["cost"] * 1.45)
                                    if item["type"] == "click":
                                        per_click += item["power"]
                                    else:
                                        per_sec += item["power"]
                                    if not was_unlocked and count_unique_cats() == 4:
                                        skins_unlocked = True
                                        write_skin_unlock(True)
                                        save_full_progress()
                                        current_skin_idx = 1
                                        big_cat = SKIN_SURFS.get("4-Cat Squad!")
                                        floating_texts.append({
                                            "text": "4-CAT SKIN UNLOCKED!",
                                            "x": float(play_center_x),
                                            "y": float(cat_rect.top - 30),
                                            "alpha": 255.0,
                                        })
                                play_sfx(buy_sound)
    if squish > 0:
        squish = max(0.0, squish - 0.12)

    for ft in floating_texts:
        ft["y"] -= 75 * dt
        ft["alpha"] -= 260 * dt
    floating_texts = [ft for ft in floating_texts if ft["alpha"] > 0]

    cur_w = int(base_w * (1 + 0.14 * squish))
    cur_h = int(base_h * (1 - 0.14 * squish))
    current_cat = pygame.transform.smoothscale(big_cat, (cur_w, cur_h))
    draw_rect = current_cat.get_rect(center=cat_rect.center)

    screen.fill(BG)
    screen.blit(current_cat, draw_rect)

    for ft in floating_texts:
        ft_surf = font_float.render(ft["text"], True, DARK_ORANGE)
        ft_surf.set_alpha(int(ft["alpha"]))
        screen.blit(ft_surf, ft_surf.get_rect(center=(int(ft["x"]), int(ft["y"]))))

    score_surf = font_big.render(f"Cats: {int(clicks):,}", True, OUTLINE)
    screen.blit(score_surf, (30, 25))

    if show_high_score and battle_phase == "solo":
        best_surf = font_med.render(f"High Score: {high_score:,}", True, DARK_ORANGE)
        screen.blit(best_surf, (30, 78))
        rate_y = 112
    else:
        rate_y = 80

    rate_surf = font_small.render(f"+{per_click:,}/click  |  +{per_sec:,}/sec", True, GREEN)
    screen.blit(rate_surf, (30, rate_y))

    if battle_phase in ("p1_turn", "p2_turn"):
        t_surf = font_big.render(f"Time: {battle_timer:0.1f}s", True, RED_BTN if battle_timer <= 5 else BLUE_BTN)
        screen.blit(t_surf, t_surf.get_rect(center=(play_center_x, 42)))

        if battle_phase == "p1_turn":
            turn_txt = "YOUR TURN! Set the score to beat!" if net_role == "host" else "WATCHING PLAYER 1 SET THE GOAL..."
            sub_txt = ""
        else:
            turn_txt = "YOUR TURN! Beat Player 1's Score!" if net_role == "client" else "WATCHING PLAYER 2..."
            sub_txt = f"Score to Beat: {p1_final_score:,} Cats"

        banner_surf = font_med.render(turn_txt, True, DARK_ORANGE if is_my_turn() else BLUE_BTN)
        screen.blit(banner_surf, banner_surf.get_rect(center=(play_center_x, 85)))
        if sub_txt:
            goal_surf = font_med.render(sub_txt, True, GREEN if int(clicks) > p1_final_score else OUTLINE)
            screen.blit(goal_surf, goal_surf.get_rect(center=(play_center_x, 120)))

    hint_surf = font_small.render("Press ESC for Options  |  Scroll Shop with Mouse Wheel", True, (150, 135, 120))
    screen.blit(hint_surf, (30, scr_h - 45))

    pygame.draw.rect(screen, SHOP_BG, (scr_w - shop_w, 0, shop_w, scr_h))
    for i, item in enumerate(shop_items):
        card_rect = shop_rects[i]
        if card_rect.bottom < 90 or card_rect.top > scr_h:
            continue
        maxed_out = item["max"] is not None and item["owned"] >= item["max"]
        can_afford = clicks >= item["cost"] and is_my_turn()
        if maxed_out:
            card_color, title_text, cost_text, cost_color = CARD_OWNED, f"{item['name']} [1/1]", "OWNED", GOLD_TEXT
        else:
            card_color = CARD_AFFORD if can_afford else CARD_LOCKED
            title_text = f"{item['name']} ({item['owned']})" if item["max"] is None else f"{item['name']} (0/1)"
            cost_text = f"Cost: {item['cost']:,} Cats"
            cost_color = GREEN if can_afford else (140, 130, 120)

        pygame.draw.rect(screen, card_color, card_rect, border_radius=14)
        pygame.draw.rect(screen, OUTLINE, card_rect, 3, border_radius=14)
        screen.blit(font_med.render(title_text, True, OUTLINE), (card_rect.x + 15, card_rect.y + 10))
        screen.blit(font_small.render(item["desc"], True, DARK_ORANGE), (card_rect.x + 15, card_rect.y + 44))
        screen.blit(font_small.render(cost_text, True, cost_color), (card_rect.x + 15, card_rect.y + 73))

    pygame.draw.rect(screen, SHOP_BG, (scr_w - shop_w, 0, shop_w, 92))
    pygame.draw.line(screen, OUTLINE, (scr_w - shop_w, 0), (scr_w - shop_w, scr_h), 4)
    shop_title = font_big.render("SHOP" if is_my_turn() else "SHOP (LOCKED)", True, OUTLINE)
    screen.blit(shop_title, shop_title.get_rect(center=(scr_w - shop_w // 2, 48)))

    if net_connected:
        screen.blit(p2_cursor, (int(partner_x * scr_w) - 2, int(partner_y * scr_h) - 16))
    if ui_screen == "game" and battle_phase == "results":
        ov = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        ov.fill((40, 30, 20, 165))
        screen.blit(ov, (0, 0))
        pygame.draw.rect(screen, BG, res_rect, border_radius=20)
        pygame.draw.rect(screen, OUTLINE, res_rect, 4, border_radius=20)

        if p2_final_score > p1_final_score:
            win_txt = "PLAYER 2 WINS!"
        elif p1_final_score > p2_final_score:
            win_txt = "PLAYER 1 (HOST) WINS!"
        else:
            win_txt = "IT'S A TIE!"

        w_s = font_big.render(win_txt, True, GOLD_TEXT)
        screen.blit(w_s, w_s.get_rect(center=(res_rect.centerx, res_rect.y + 55)))
        p1_s = font_med.render(f"Player 1 Score: {p1_final_score:,} Cats", True, OUTLINE)
        p2_s = font_med.render(f"Player 2 Score: {p2_final_score:,} Cats", True, BLUE_BTN)
        screen.blit(p1_s, p1_s.get_rect(center=(res_rect.centerx, res_rect.y + 125)))
        screen.blit(p2_s, p2_s.get_rect(center=(res_rect.centerx, res_rect.y + 170)))

        if net_role == "host":
            pygame.draw.rect(screen, GREEN, btn_rematch, border_radius=12)
            pygame.draw.rect(screen, OUTLINE, btn_rematch, 3, border_radius=12)
            rm_l = font_med.render("Play Again (Same Time)", True, WHITE)
            screen.blit(rm_l, rm_l.get_rect(center=btn_rematch.center))

        pygame.draw.rect(screen, CARD_AFFORD, btn_res_lobby, border_radius=12)
        pygame.draw.rect(screen, OUTLINE, btn_res_lobby, 3, border_radius=12)
        bl_l = font_med.render("Return to Lobby", True, OUTLINE)
        screen.blit(bl_l, bl_l.get_rect(center=btn_res_lobby.center))

    elif ui_screen == "options":
        ov = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        ov.fill((40, 30, 20, 150))
        screen.blit(ov, (0, 0))
        pygame.draw.rect(screen, BG, opt_rect, border_radius=20)
        pygame.draw.rect(screen, OUTLINE, opt_rect, 4, border_radius=20)
        o_s = font_big.render("OPTIONS", True, OUTLINE)
        screen.blit(o_s, o_s.get_rect(center=(opt_rect.centerx, opt_rect.y + 42)))

        cur_name = get_skin_by_idx(current_skin_idx)
        skin_lbl = f"Skin: {cur_name}" if all_four_unlocked() else f"Skin: Locked ({count_unique_cats()}/4 Cats)"
        opt_btns = [
            (btn_resume, "Resume Game", CARD_AFFORD, OUTLINE),
            (btn_open_lobby, "Multiplayer Lobby", BLUE_BTN, WHITE),
            (btn_skin, skin_lbl, CARD_OWNED if all_four_unlocked() else CARD_LOCKED, GOLD_TEXT if all_four_unlocked() else OUTLINE),
            (btn_sound, f"Sound Effects: {'ON' if sound_enabled else 'OFF'}", CARD_AFFORD, GREEN if sound_enabled else DARK_ORANGE),
            (btn_toggle_hs, f"Show High Score: {'ON' if show_high_score else 'OFF'}", CARD_AFFORD, GREEN if show_high_score else DARK_ORANGE),
            (btn_reset_hs, "Reset High Score", WARN_BTN, WHITE),
            (btn_save, "Save Solo Progress", CARD_AFFORD, OUTLINE),
            (btn_load, "Load Solo Progress", CARD_AFFORD, OUTLINE),
            (btn_fullscreen, f"Fullscreen: {'ON' if is_fullscreen else 'OFF'}", CARD_AFFORD, GREEN if is_fullscreen else DARK_ORANGE),
            (btn_exit, "Exit Game", RED_BTN, WHITE),
        ]
        for rect, lbl, bg_c, tx_c in opt_btns:
            pygame.draw.rect(screen, bg_c, rect, border_radius=12)
            pygame.draw.rect(screen, OUTLINE, rect, 3, border_radius=12)
            s = font_med.render(lbl, True, tx_c)
            screen.blit(s, s.get_rect(center=rect.center))

        if status_msg:
            ms = font_small.render(status_msg, True, GREEN)
            screen.blit(ms, ms.get_rect(center=(opt_rect.centerx, opt_rect.bottom - 22)))

    elif ui_screen == "lobby":
        ov = pygame.Surface((scr_w, scr_h), pygame.SRCALPHA)
        ov.fill((40, 30, 20, 165))
        screen.blit(ov, (0, 0))
        pygame.draw.rect(screen, BG, lob_rect, border_radius=20)
        pygame.draw.rect(screen, OUTLINE, lob_rect, 4, border_radius=20)

        t_s = font_big.render("MULTIPLAYER LOBBY", True, OUTLINE)
        screen.blit(t_s, t_s.get_rect(center=(lob_rect.centerx, lob_rect.y + 44)))

        ip_info = f"Your Local IP: {get_local_ip()}  |  Status: {'Connected!' if net_connected else net_role.upper()}"
        i_s = font_small.render(ip_info, True, GREEN if net_connected else DARK_ORANGE)
        screen.blit(i_s, i_s.get_rect(center=(lob_rect.centerx, lob_rect.y + 88)))

        c_lbl = "Close Host Lobby" if net_role == "host" else "Create Lobby (Host)"
        j_lbl = f"IP: {ip_input}_" if typing_mode == "ip" else ("Leave Lobby" if net_role == "client" else "Join Lobby (Enter IP)")
        p_lbl = f"Preset: {battle_duration}s"
        cu_lbl = f"Time: {custom_time_input}_" if typing_mode == "custom_time" else "Custom Time"

        lob_btns = [
            (btn_create_lob, c_lbl, BLUE_BTN if net_role == "host" else CARD_AFFORD, WHITE if net_role == "host" else BLUE_BTN),
            (btn_join_lob, j_lbl, BLUE_BTN if (net_role == "client" or typing_mode == "ip") else CARD_AFFORD, WHITE if (net_role == "client" or typing_mode == "ip") else BLUE_BTN),
            (btn_preset_time, p_lbl, CARD_AFFORD if net_role != "client" else CARD_LOCKED, OUTLINE),
            (btn_custom_time, cu_lbl, WARN_BTN if typing_mode == "custom_time" else (CARD_AFFORD if net_role != "client" else CARD_LOCKED), WHITE if typing_mode == "custom_time" else OUTLINE),
        ]
        for rect, lbl, bg_c, tx_c in lob_btns:
            pygame.draw.rect(screen, bg_c, rect, border_radius=12)
            pygame.draw.rect(screen, OUTLINE, rect, 3, border_radius=12)
            s = font_med.render(lbl, True, tx_c)
            screen.blit(s, s.get_rect(center=rect.center))

        can_start = (net_role == "host" and net_connected)
        pygame.draw.rect(screen, GREEN if can_start else CARD_LOCKED, btn_start_battle, border_radius=12)
        pygame.draw.rect(screen, OUTLINE, btn_start_battle, 3, border_radius=12)
        st_txt = "START BATTLE!" if can_start else ("Waiting for Host to Start..." if net_role == "client" else "Waiting for Player 2 to Join...")
        st_s = font_med.render(st_txt, True, WHITE if can_start else (130, 120, 110))
        screen.blit(st_s, st_s.get_rect(center=btn_start_battle.center))

        pygame.draw.rect(screen, CARD_AFFORD, btn_back_solo, border_radius=12)
        pygame.draw.rect(screen, OUTLINE, btn_back_solo, 3, border_radius=12)
        bk_s = font_med.render("Back to Solo Game", True, OUTLINE)
        screen.blit(bk_s, bk_s.get_rect(center=btn_back_solo.center))

        if status_msg:
            ms = font_small.render(status_msg, True, GREEN)
            screen.blit(ms, ms.get_rect(center=(lob_rect.centerx, lob_rect.bottom - 35)))

    mx, my = pygame.mouse.get_pos()
    screen.blit(fish_cursor, (mx - 2, my - 16))

    pygame.display.flip()
