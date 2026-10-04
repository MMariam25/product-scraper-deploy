import json
import streamlit as st
import pandas as pd
from scraper import scrape_url

st.set_page_config(page_title="Product Scraper", page_icon="🛍️", layout="wide")

st.title("🛍️ Product Scraper")
st.markdown("Enter one or more product URLs (one per line) and extract product data instantly.")

urls_input = st.text_area(
    "Product URLs",
    placeholder="https://example.com/product/sneakers\nhttps://example.com/product/bag",
    height=130,
)

if st.button("Scrape", type="primary"):
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        all_results = []
        progress = st.progress(0, text="Starting…")
        for i, url in enumerate(urls):
            progress.progress(i / len(urls), text=f"Scraping {url}")
            try:
                results = scrape_url(url)
                all_results.extend(results)
            except Exception as e:
                st.error(f"❌ Failed for `{url}`: {e}")
        progress.progress(1.0, text="Done!")

        if all_results:
            st.divider()
            st.subheader(f"{len(all_results)} product(s) found")

            cols = st.columns(min(4, len(all_results)))
            for i, product in enumerate(all_results):
                with cols[i % len(cols)]:
                    if product.get("image"):
                        try:
                            st.image(product["image"], use_container_width=True)
                        except Exception:
                            pass
                    st.markdown(f"**{product.get('name', '—')}**")
                    if product.get("price"):
                        st.markdown(f"`{product['price']}`")
                    if product.get("description"):
                        st.caption(product["description"][:120] + "…" if len(product.get("description","")) > 120 else product.get("description",""))
                    st.markdown(f"[View product]({product['url']})")

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "⬇️ Download CSV",
                    pd.DataFrame(all_results).to_csv(index=False),
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
