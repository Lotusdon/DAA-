"""
Streamlit interface for the Divide and Conquer assignment.

Run from the project folder:
    pip install streamlit matplotlib
    streamlit run main.py

Put cp*.txt files in datasets/closest_pair/ and im*.txt files in
datasets/multiplication/. You can also upload a file directly.
"""
from pathlib import Path
from time import perf_counter

import streamlit as st
import matplotlib.pyplot as plt

from algorithms.closest_pair import closest_pair, read_points_file
from algorithms.karatsuba import karatsuba_multiply, read_multiplication_file


ROOT = Path(__file__).resolve().parent
CP_DIR = ROOT / "datasets" / "closestpair"
IM_DIR = ROOT / "datasets" / "multiplication"

st.set_page_config(page_title="Divide and Conquer Visualizer",
                   page_icon="ðŸ§ ", layout="wide")

st.title("ðŸ§  Divide and Conquer Algorithm Visualizer")
st.caption("Closest Pair of Points Â· Karatsuba Integer Multiplication")

tab_cp, tab_karatsuba = st.tabs(["ðŸ“ Closest Pair of Points", "âœ–ï¸ Karatsuba Multiplication"])


def choose_input(label: str, folder: Path, file_prefix: str):
    files = sorted(folder.glob(f"{file_prefix}*.txt")) if folder.exists() else []
    names = ["Upload a file"] + [str(p) for p in files]
    choice = st.selectbox(label, names, key=f"{file_prefix}_file_choice")
    uploaded = None
    if choice == "Upload a file":
        uploaded = st.file_uploader("Upload a plain-text input file",
                                    type=["txt"], key=f"{file_prefix}_upload")
        if uploaded is None:
            return None
        temp_path = ROOT / f"_uploaded_{file_prefix}.txt"
        temp_path.write_bytes(uploaded.getvalue())
        return temp_path
    return Path(choice)


with tab_cp:
    st.subheader("Closest Pair of Points â€” O(n log n)")
    st.write("Choose a cp dataset. Small datasets can record recursion summaries; "
             "large datasets should run without collecting animation steps.")
    cp_path = choose_input("Select closest-pair dataset", CP_DIR, "cp")

    if cp_path is not None:
        collect_cp_steps = st.checkbox("Collect step summaries (recommended only for small files)",
                                       value=False, key="cp_steps")
        if st.button("Run Closest Pair", type="primary", key="run_cp"):
            try:
                points = read_points_file(str(cp_path))
                start = perf_counter()
                point_a, point_b, distance, steps = closest_pair(
                    points, collect_steps=collect_cp_steps
                )
                elapsed = perf_counter() - start

                st.success("Closest pair found.")
                c1, c2, c3 = st.columns(3)
                c1.metric("Number of points", f"{len(points):,}")
                c2.metric("Minimum distance", f"{distance:.12g}")
                c3.metric("Execution time", f"{elapsed:.6f} seconds")
                st.write(f"**Point A:** `{point_a}`")
                st.write(f"**Point B:** `{point_b}`")

                # Avoid trying to draw millions of points in the browser.
                if len(points) <= 20_000:
                    fig, ax = plt.subplots()
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    ax.scatter(xs, ys, s=12, label="Input points")
                    ax.scatter([point_a[0], point_b[0]],
                               [point_a[1], point_b[1]],
                               s=90, marker="x", label="Closest pair")
                    ax.plot([point_a[0], point_b[0]],
                            [point_a[1], point_b[1]], linewidth=2)
                    ax.set_xlabel("X")
                    ax.set_ylabel("Y")
                    ax.set_title("Closest Pair Result")
                    ax.legend()
                    ax.grid(True, alpha=0.25)
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    st.info("Graph hidden because this dataset is very large.")

                if steps:
                    st.markdown("#### Algorithm step summaries")
                    st.caption("These are recursion-level summaries, not an animation of every comparison.")
                    for index, step in enumerate(steps, start=1):
                        with st.expander(f"Step {index}: {step['type'].replace('_', ' ').title()}"):
                            st.json(step)
                st.session_state["cp_last_result"] = {
                    "point_a": point_a, "point_b": point_b,
                    "distance": distance, "elapsed": elapsed
                }
            except Exception as error:
                st.error(f"Could not process this file: {error}")


with tab_karatsuba:
    st.subheader("Karatsuba Integer Multiplication")
    st.write("Choose an im dataset containing exactly two non-negative integers.")
    im_path = choose_input("Select multiplication dataset", IM_DIR, "im")

    if im_path is not None:
        collect_im_steps = st.checkbox("Collect recursive step summaries (small inputs only)",
                                       value=False, key="im_steps")
        if st.button("Run Karatsuba", type="primary", key="run_im"):
            try:
                number_a, number_b = read_multiplication_file(str(im_path))
                start = perf_counter()
                product, steps = karatsuba_multiply(
                    number_a, number_b, collect_steps=collect_im_steps
                )
                elapsed = perf_counter() - start

                st.success("Multiplication completed.")
                c1, c2, c3 = st.columns(3)
                c1.metric("Digits in A", f"{len(number_a):,}")
                c2.metric("Digits in B", f"{len(number_b):,}")
                c3.metric("Execution time", f"{elapsed:.6f} seconds")
                st.write("**Number A:**")
                st.code(number_a if len(number_a) <= 500 else
                        f"{number_a[:250]} ... {number_a[-250:]}")
                st.write("**Number B:**")
                st.code(number_b if len(number_b) <= 500 else
                        f"{number_b[:250]} ... {number_b[-250:]}")
                st.write(f"**Product digits:** {len(product):,}")
                st.write("**Final product:**")
                st.code(product if len(product) <= 2_000 else
                        f"{product[:1_000]} ... {product[-1_000:]}")

                if steps:
                    st.markdown("#### Karatsuba recursion steps")
                    st.caption("For readability, large intermediate values may be lengthy.")
                    for index, step in enumerate(steps, start=1):
                        with st.expander(f"Step {index}: {step['type'].title()} (depth {step['depth']})"):
                            st.json(step)
            except Exception as error:
                st.error(f"Could not process this file: {error}")

st.divider()
st.caption("For large datasets, disable step collection. The assignment requires step-by-step "
           "demonstrations for small inputs and final results plus timing for large inputs.")

