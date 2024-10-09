import streamlit as st
from helpers import create_docs

def main():
    st.set_page_config(page_title="Bill Extractor")
    st.title("Bill Extractor AI Assistant 🧾")

    # Upload Bills
    pdf_files = st.file_uploader("Upload your bills in PDF format only", type=["pdf"], accept_multiple_files=True)
    extract_button = st.button("Extract Bill Data")

    if extract_button and pdf_files:
        with st.spinner("Extracting... This may take some time..."):
            try:
                data_frame = create_docs(pdf_files)

                if not data_frame.empty:
                    st.write(data_frame.head())
                    data_frame["AMOUNT"] = data_frame["AMOUNT"].astype(float)

                    avg_amount = data_frame['AMOUNT'].mean()
                    st.write("Average Bill Amount: ", avg_amount)

                    # Convert to CSV
                    csv_data = data_frame.to_csv(index=False).encode("utf-8")

                    st.download_button(
                        "Download Data as CSV",
                        csv_data,
                        "CSV_Bills.csv",
                        "text/csv",
                        key="download-csv"
                    )
                else:
                    st.warning("No data extracted from the uploaded files.")
            except Exception as e:
                st.error(f"An error occurred during extraction: {e}")
        st.success("Extraction completed successfully!")

# Invoking main function
if __name__ == '__main__':
    main()
