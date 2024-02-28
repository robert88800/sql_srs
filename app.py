# pylint: disable=missing-module-docstring

import os
import logging
import duckdb
import streamlit as st

if "data" not in os.listdir():
    logging.error(os.listdir())
    logging.error("creating folder data")
    os.mkdir("data")

if "exercises_sql_tables.duckdb" not in os.listdir("data"):
    exec(open("init_db.py").read())
    # subprocess.run(["python", "init_db.py"])

con = duckdb.connect(database="data/exercises_sql_tables.duckdb", read_only=False)

with st.sidebar:
    theme = st.selectbox(
        "What would you like to review ?",
        ("cross_joins", "GroupBy", "window_functions"),
        index=None,
        placeholder="Select a theme...",
    )
    st.write("You selected :", theme)

    if theme:
        exercise = (
            con.execute(f"SELECT * FROM memory_state WHERE theme = '{theme}'")
            .df()
            .sort_values("last_reviewed")
            .reset_index()
        )
        st.write(exercise)

        exercise_name = exercise.loc[0, "exercise_name"]
        with open(f"answers/{exercise_name}.sql", "r", encoding="utf-8") as f:
            answer = f.read()

        solution_df = con.execute(answer).df()

st.header("Entrez votre code : ")
query = st.text_area(key="user_input", label="Renseignez votre code SQL ici : ")
if query:
    result = con.execute(query).df()
    st.dataframe(result)

    if theme:
        try:
            result = result[solution_df.columns]
            st.dataframe(result.compare(solution_df))
        except KeyError as e:
            st.write("Some columns are missing")

        n_lines_difference = result.shape[0] - solution_df.shape[0]
        if n_lines_difference != 0:
            st.write(
                f"result has a {n_lines_difference} lines difference with the solution"
            )


tab2, tab3 = st.tabs(["Tables", "Solution"])

with tab2:
    if theme:
        exercise_tables = exercise.loc[0, "tables"]
        for table in exercise_tables:
            st.write(f"table : {table}")
            df_table = con.execute(f"SELECT * FROM {table}").df()
            st.dataframe(df_table)

with tab3:
    if theme:
        st.write(answer)
