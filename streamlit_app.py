# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(f"Customize Your Smoothie :cup_with_straw: {st.__version__}")
st.write(
  """
  Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

my_new_dataframe = session.table("smoothies.public.orders") \
    .filter(col("ORDER_FILLED") == 0) \
    .collect()

if my_new_dataframe:
    editable_df = st.data_editor(my_new_dataframe)
    submitted = st.button('Submit')
    if(submitted):

        try:
            og_dataset = session.table("smoothies.public.orders")
            edited_dataset = session.create_dataframe(editable_df)
            og_dataset.merge(edited_dataset
                             , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
                             , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                            )
            st.write('Orders updated!')
        except:
            st.write('Something went wrong!')
            
ingredients = st.multiselect(
    "Choose up to 5 ingredients:?",
    my_dataframe,

    max_selections=5
)

if ingredients:
    ingredients_string = ''

    for fruit_chosen in ingredients:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)
    
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '"""+name_on_order+"""')"""

    time_to_insert = st.button('Submit order')
    
    # st.write(my_insert_stmt)
    if ingredients_string and time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
st_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
