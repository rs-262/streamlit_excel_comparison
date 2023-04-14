import streamlit as st
import pandas as pd

#st.set_page_config(layout="wide")

# st.markdown(
#     """
#     <style>
#     .body {background-color:lightblue;} 
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# LINK TO THE CSS FILE
with open('style.css') as f:
 st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

st.title('Excel File Comparison App')
st.divider()

# side bar
with st.sidebar:
    st.write("add content here")


st.subheader("Drop the current months file here:")

with st.container():
    # widget for uploading current month file
    current_month_file = st.file_uploader('Upload a file',key='current')

    # if else to display dataframe head if uploaded
    if not current_month_file: # if false
        st.write("No file uploaded yet")
    elif current_month_file: # if true
        current_string = current_month_file.name # gets file name as string
        # validates that it's an excel file 
        if current_string.lower().endswith(('.xls', '.xlsx', '.xlsm')):
            current_month_df = pd.read_excel(current_month_file)
            st.write(current_month_df.head(1))
        else:
            st.write('<p style="color:red;">File type is invalid please upload an excel file with exension .xls, .xlsx or .xlsm</p>', 
            unsafe_allow_html=True)

st.divider()


st.subheader("Drop the previous months file here")

# widget for uploading current month file
previous_month_file = st.file_uploader('Upload a file',key='previous')

# if else to display dataframe head if uploaded
if not previous_month_file:
    st.write("No file uploaded yet")
elif previous_month_file:
    previous_string = previous_month_file.name # gets file name as string
    # validates that it's an excel file 
    if previous_string.lower().endswith(('.xls', '.xlsx', '.xlsm')):
        previous_month_df = pd.read_excel(previous_month_file)
        st.write(previous_month_df.head(1))
    else:
        st.write('<p style="color:red;">File type is invalid please upload an excel file with exension .xls, .xlsx or .xlsm</p>', 
        unsafe_allow_html=True)


st.divider()

# function for comparing the file

def compare_file(current,previous):

    # sets the proeprty ref/unit ref of last row which is the totals row to 9999. This is so when
    # converting the data type before joining it wont cause errors
    current.at[current.shape[0]-1,'Property Ref'] = 9999
    current.at[current.shape[0]-1,'Unit ID'] = 9999
    previous.at[previous.shape[0]-1,'Property Ref'] = 9999
    previous.at[previous.shape[0]-1,'Unit ID'] = 9999

    # Changes data type of property ref and unit ref
    current = current.astype({'Property Ref': 'int64', 'Unit ID': 'int64'})
    previous = previous.astype({'Property Ref': 'int64', 'Unit ID': 'int64'})

    #adds unique ref for df1 - concats property and unit ref
    current['unique_ref'] = current['Property Ref'].astype(str)+current['Unit ID'].astype(str)
    current['unique_ref'] = current['unique_ref'].astype(int)
    #current['unique_ref']

    #adds unique ref for df2 - concats property and unit ref
    previous['unique_ref'] = previous['Property Ref'].astype(str)+previous['Unit ID'].astype(str)
    previous['unique_ref'] = previous['unique_ref'].astype(int)
    #previous['unique_ref']

    #changes index to unique ref, this makes join work 
    current.set_index('unique_ref',inplace=True)
    previous.set_index('unique_ref',inplace=True)

    #filling NaN with 'Null' - this will help when comparing later - in pandas Nan == Nan is False but I want this to be True
    # If you compare Null == Null it's True
    current = current.fillna('Null')
    previous = previous.fillna('Null')

    #create a list of the column names of df1 to use later
    current_columns = current.columns
    current_columns = current_columns.tolist()

    #create a list of the column names of df2 to use later
    previous_columns = previous.columns
    previous_columns = previous_columns.tolist()

    #this loop concatenates '_old to end of string so when comparing the column names in the joined df we can use these'
    n = 0
    for i in previous_columns:
        previous_columns[n] = previous_columns[n]+'_old'
        n = n+1

    # this joins the to data sets, it uses the index (which was set to to the uniqe ref above)
    df_joined = current.join(previous, rsuffix='_old')

    # variable for total column numbers
    current_columns_len = current.shape[1]

    # variable for total row number
    current_rows_len = current.shape[0]

    #this does the comparison
    #test how this works with columns in different orders and different number of columns
    for index, row in df_joined.iterrows():
        for i in range(0,current_columns_len-1):
            if df_joined.loc[index,current_columns[i]] == df_joined.loc[index,previous_columns[i]]:
                df_joined.loc[index,current_columns[i]] = df_joined.loc[index,current_columns[i]]
            else:
                df_joined.loc[index,current_columns[i]] = str(df_joined.loc[index,current_columns[i]])+'-->'+str(df_joined.loc[index,previous_columns[i]])

    # Drops the columns from the previous months DF
    df_joined = pd.DataFrame(df_joined.drop(columns=previous_columns))

    # create a style function to apply conditional formatting
    def highlight_cell(cell):
        if '-->' in str(cell):
            return 'background-color: yellow'
        else:
            return ''

    # apply the style function to the DataFrame
    styled_df = df_joined.style.applymap(highlight_cell)

    return styled_df


st.subheader("Click Button to run comparison")
run_comparison = st.button("run comparison")

st.write(run_comparison)

# this performs action when button is clicked
if run_comparison:
    output_df = compare_file(current_month_df,previous_month_df)
    st.write(output_df)
else:
    st.write("")


    # this prints to excel
   # styled_df.to_excel(f'U:\Data Files\Python Files\File Comparison\Excel_diff{datetime.now().strftime("_%d-%m-%Y-%H-%M-%S")}.xlsx',index=False,header=True)




