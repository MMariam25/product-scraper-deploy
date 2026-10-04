import json
import streamlit as st
import pandas as pd
from scraper import Scraper

st.set_page_config(page_title="Product Scraper", page_icon="🛍️", layout="wide")

st.title("🛍️ Product Scraper")
st.markdown("Scrape product data from **ygshoes188.com** — shoes, bags and accessories.")

CATEGORIES = {
    "Shoes": ("shoes", "http://shoes.ygshoes188.com/"),
    "Bags": ("bags", "http://bags.ygshoes188.com/"),
    "Accessories": ("acc", "http://acc.ygshoes188.com/"),
}

selected = st.multiselect(
    "Select categories to scrape",
    list(CATEGORIES.keys()),
    default=["Shoes"],
)

if st.button("Start Scraping", type="primary", disabled=not selected):
    all_results = []
    progress = st.progress(0, text="Starting...")

    for idx, category in enumerate(selected):
        product_key, url = CATEGORIES[category]
        progress.progress((idx) / len(selected), text=f"Scraping {category}...")
        with st.spinner(f"Fetching {category}..."):
            try:
                s = Scraper(product_key, url)
                results = s.run()
                all_results.extend(results)
                st.success(f"✅ {category}: {len(results)} products found")
            except Exception as e:
                st.error(f"❌ {category}: failed — {e}")

    progress.progress(1.0, text="Done!")

    if all_results:
        st.divider()
        st.subheader(f"Results — {len(all_results)} products")

        cols = st.columns(4)
        for i, product in enumerate(all_results):
            with cols[i % 4]:
                image_url = product.get("image") or product.get("category-image")
                if image_url:
                    try:
                        st.image(image_url, use_container_width=True)
                    except Exception:
                        st.markdown("_(no image)_")
                name = product.get("Name") or product.get("category", "Unknown")
                price = product.get("Price", "")
                st.caption(f"**{name}**" + (f"  \n{price}" if price else ""))

        st.divider()
        st.subheader("Download")
        col1, col2 = st.columns(2)
        with col1:
            df = pd.DataFrame(all_results)
            st.download_button(
                "⬇️ Download CSV",
                df.to_csv(index=False),
                "products.csv",
                "text/csv",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "⬇️ Download JSON",
                json.dumps(all_results, indent=2, ensure_ascii=False),
                "products.json",
                "application/json",
                use_container_width=True,
            )
    else:
        st.warning("No products found. The target site may be temporarily unavailable — try again later.")
