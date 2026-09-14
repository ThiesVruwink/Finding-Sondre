import base64
from pathlib import Path
import random
import streamlit as st

st.set_page_config(
    page_title="Sondre Ørjasæter game",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = Path(__file__).parent
BASE_EMOJI = BASE_DIR / "base_emoji.webp"
SAFE_REVEAL = BASE_DIR / "safe_reveal.jpg"
LOSE_REVEAL = BASE_DIR / "lose_reveal.jpg"
WIN_REVEAL = BASE_DIR / "ballon_dor.png"


def get_base64_image(image_input):
    """Converts a Path, str, or bytes into a base64 data URI."""
    if isinstance(image_input, (str, Path)):
        p = Path(image_input)
        if not p.exists():
            return ""
        with open(p, "rb") as f:
            data = f.read()
    elif isinstance(image_input, bytes):
        data = image_input
    else:
        return ""
    encoded = base64.b64encode(data).decode()
    return f"data:image/webp;base64,{encoded}"


def init_state():
    defaults = {
        "images_safe": [SAFE_REVEAL],
        "image_loser": LOSE_REVEAL,
        "image_winner": WIN_REVEAL,
        "board": None,
        "game_over": False,
        "won": False,
        "num_tiles": 12,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def build_board(n):
    safe_pool = st.session_state.images_safe or [SAFE_REVEAL]

    tiles = []
    for i in range(n - 1):
        tiles.append(
            {
                "type": "safe",
                "image": safe_pool[i % len(safe_pool)],
                "revealed": False,
            }
        )

    tiles.append(
        {
            "type": "loser",
            "image": st.session_state.image_loser or LOSE_REVEAL,
            "revealed": False,
        }
    )

    random.shuffle(tiles)
    return tiles


def new_game():
    st.session_state.board = build_board(st.session_state.num_tiles)
    st.session_state.game_over = False
    st.session_state.won = False


init_state()

st.title("Sondre Ørjasæter")
st.caption("Open boxes to find superstar winger Sondre Ørjasæter, lose when generational loser Jakob Trenskow is found"
)

with st.sidebar:
    st.header("Setup")
    st.write(
        "De standaardafbeeldingen zitten in de app en werken dus ook online. "
        "Je kunt ze hieronder eventueel vervangen."
    )

    safe_uploads = st.file_uploader(
        "Extra veilige foto's",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        accept_multiple_files=True,
        key="safe_uploader",
    )

    loser_upload = st.file_uploader(
        "Nieuwe LOSER-foto",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        accept_multiple_files=False,
        key="loser_uploader",
    )

    winner_upload = st.file_uploader(
        "Nieuwe Ballon d'Or Win-foto",
        type=["png", "jpg", "jpeg", "gif", "webp"],
        accept_multiple_files=False,
        key="winner_uploader",
    )

    num_tiles = st.slider(
        "Number of boxes",
        min_value=6,
        max_value=24,
        value=st.session_state.num_tiles,
        step=1,
    )

    if safe_uploads:
        st.session_state.images_safe = [SAFE_REVEAL] + [
            f.getvalue() for f in safe_uploads
        ]

    if loser_upload:
        st.session_state.image_loser = loser_upload.getvalue()

    if winner_upload:
        st.session_state.image_winner = winner_upload.getvalue()

    settings_changed = num_tiles != st.session_state.num_tiles
    st.session_state.num_tiles = num_tiles

    if (
        st.button("🔀 New Game", use_container_width=True)
        or st.session_state.board is None
        or settings_changed
    ):
        new_game()

# Base emoji data URI
base_emoji_b64 = get_base64_image(BASE_EMOJI)

# Force multi-column layout on mobile and prevent vertical stacking
st.markdown(
    f"""
    <style>
    /* Prevent Streamlit from collapsing columns into a single vertical stack on mobile */
    div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 8px !important;
    }}

    div[data-testid="stColumn"] {{
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: auto !important;
    }}

    /* Button base styles */
    div[data-testid="stColumn"] button {{
        background-image: url("{base_emoji_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        height: 110px !important;
        width: 100% !important;
        min-width: 0px !important;
        padding: 0 !important;
    }}

    div[data-testid="stColumn"] button:hover {{
        transform: scale(1.03);
    }}

    div[data-testid="stColumn"] button p {{
        display: none !important;
    }}

    /* Image base styles */
    div[data-testid="stColumn"] img {{
        border-radius: 8px !important;
        height: 110px !important;
        object-fit: cover !important;
        width: 100% !important;
    }}

    /* Mobile screens: adjust heights so square ratio holds without overflowing */
    @media (max-width: 768px) {{
        div[data-testid="stHorizontalBlock"] {{
            gap: 6px !important;
            margin-bottom: 6px !important;
        }}
        div[data-testid="stColumn"] button {{
            height: 76px !important;
            border-radius: 6px !important;
        }}
        div[data-testid="stColumn"] img {{
            height: 76px !important;
            border-radius: 6px !important;
        }}
        div[data-testid="stColumn"] div[data-testid="stCaptionContainer"] p {{
            font-size: 0.75rem !important;
            text-align: center !important;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

board = st.session_state.board

cols_per_row = 4
rows = (len(board) + cols_per_row - 1) // cols_per_row

idx = 0
for _ in range(rows):
    cols = st.columns(cols_per_row)

    for col in cols:
        if idx >= len(board):
            break

        tile = board[idx]

        with col:
            if tile["revealed"]:
                st.image(tile["image"], use_container_width=True)

                if tile["type"] == "loser":
                    st.error("You found the loser.")
                else:
                    st.caption("✅ Safe!")

            else:
                clicked = st.button(
                    label=" ",
                    key=f"tile_{idx}",
                    disabled=st.session_state.game_over,
                    use_container_width=True,
                    help="Click to reveal",
                )

                if clicked:
                    tile["revealed"] = True

                    if tile["type"] == "loser":
                        st.session_state.game_over = True
                        st.session_state.won = False

                    elif all(
                        t["revealed"] or t["type"] == "loser"
                        for t in board
                    ):
                        st.session_state.game_over = True
                        st.session_state.won = True

                    st.rerun()

        idx += 1

st.divider()

if st.session_state.game_over:
    if st.session_state.won:
        st.success("🎉 You cleared every safe box! Sondre wins the Ballon d'Or!")
        
        # Display victory image
        win_img = st.session_state.image_winner
        if isinstance(win_img, Path) and win_img.exists():
            st.image(win_img, caption="🏆 Ballon d'Or Winner!", use_container_width=True)
        elif isinstance(win_img, bytes):
            st.image(win_img, caption="🏆 Ballon d'Or Winner!", use_container_width=True)
            
        st.balloons()
    else:
        st.error(" You touched the angry one! Game over.")

    if st.button("Play Again", use_container_width=True):
        new_game()
        st.rerun()
else:
    remaining_safe = sum(
        1
        for t in board
        if t["type"] == "safe" and not t["revealed"]
    )
    st.info(f"Boxes left to safely reveal: {remaining_safe}")
