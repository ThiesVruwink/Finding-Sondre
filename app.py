import base64
from pathlib import Path
import random
import streamlit as st

st.set_page_config(page_title="Sondre Ørjasæter game", layout="wide")

BASE_DIR = Path(__file__).parent
BASE_EMOJI = BASE_DIR / "base_emoji.webp"
SAFE_REVEAL = BASE_DIR / "safe_reveal.jpg"
LOSE_REVEAL = BASE_DIR / "lose_reveal.jpg"


def get_base64_image(image_input):
    """Converts a Path, str, or bytes into a base64 data URI."""
    if isinstance(image_input, (str, Path)):
        with open(image_input, "rb") as f:
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
st.caption(
    "Open the boxes to find the GOAT "
    "made specially for number 1 Sondre Ørjasæter fan TM"
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

    settings_changed = num_tiles != st.session_state.num_tiles
    st.session_state.num_tiles = num_tiles

    if (
        st.button("🔀 New Game", use_container_width=True)
        or st.session_state.board is None
        or settings_changed
    ):
        new_game()

# Prepare base emoji data URI once
base_emoji_b64 = get_base64_image(BASE_EMOJI)

# Inject CSS to make Streamlit buttons display the emoji directly
st.markdown(
    f"""
    <style>
    div[data-testid="stColumn"] button.emoji-btn {{
        background-image: url("{base_emoji_b64}") !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        height: 120px !important;
        width: 100% !important;
        transition: transform 0.1s ease;
    }}
    div[data-testid="stColumn"] button.emoji-btn:hover {{
        transform: scale(1.04);
    }}
    div[data-testid="stColumn"] button.emoji-btn p {{
        display: none !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

board = st.session_state.board

cols_per_row = 6
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
                # Button styled as the emoji via custom class
                clicked = st.button(
                    label=" ",
                    key=f"tile_{idx}",
                    disabled=st.session_state.game_over,
                    use_container_width=True,
                    help="Click to reveal",
                )
                
                # Tag the button with the custom CSS class
                st.markdown(
                    f"""<script>
                    var btns = window.parent.document.querySelectorAll('button[kind="secondary"]');
                    </script>""",
                    unsafe_allow_html=True,
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
        st.success("🎉 You cleared every safe box! You win!")
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
    
