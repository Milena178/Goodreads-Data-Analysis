import streamlit as st
import pandas as pd

st.set_page_config(
    page_title='GoodReads Genre-Wechsel Analyse',
    page_icon='📚',
    layout='wide'
)

@st.cache_data
def load_data():
    df = pd.read_csv('src/GoodReads_clean.csv')

    def extrahiere_erstes_genre(genre_text):
        return genre_text.split(',')[0]

    def finde_haeufigstes_genre(genres):
        return genres.value_counts().idxmax()

    df['buch_genre'] = df['genre'].apply(extrahiere_erstes_genre)
    stammgenre = df.groupby('author')['buch_genre'].agg(finde_haeufigstes_genre)
    df['stammgenre_autor'] = df['author'].map(stammgenre)
    df['ist_genrewechsel'] = df['buch_genre'] != df['stammgenre_autor']
    return df

@st.cache_data
def load_results():
    return pd.read_csv('src/genre_switch_results.csv')

df = load_data()
results = load_results()

# SIDEBAR FILTER
st.sidebar.title('🔍 Filter')

min_buecher = st.sidebar.slider(
    'Mindestanzahl Bücher pro Autor:',
    min_value=5,
    max_value=int(df['author'].value_counts().max() -1),
    value=5
)

autoren_counts = df['author'].value_counts()
gefilterte_autoren = autoren_counts[autoren_counts >= min_buecher].index
df = df[df['author'].isin(gefilterte_autoren)]
results = results[results['author'].isin(gefilterte_autoren)]

genres_liste = ['Alle'] + sorted(df['stammgenre_autor'].dropna().unique().tolist())
genre_filter = st.sidebar.selectbox('Hauptgenre filtern:', genres_liste)

if genre_filter != 'Alle':
    df = df[df['stammgenre_autor'] == genre_filter]
    passende_autoren = df['author'].unique()
    results = results[results['author'].isin(passende_autoren)]


# TITEL
st.title('📚 Genre-Wechsel bei Buchautoren')
st.subheader('Inwiefern beeinflusst ein Genrewechsel die Lesebewertungen von Buchautoren?')
st.markdown('*Analyse auf Basis von 100k GoodReads Büchern*')
st.markdown('---')


# KENNZAHLEN
anzahl_besser     = (results['Differenz'] > 0).sum()
anzahl_schlechter = (results['Differenz'] < 0).sum()
gesamt            = len(results)

col1, col2, col3, col4 = st.columns(4)
col1.metric('📖 Bücher gesamt',       f"{len(df):,}")
col2.metric('✍️ Autoren mit Wechsel', f"{gesamt:,}")
col3.metric('⬆️ Wechsel besser',      f"{anzahl_besser} ({anzahl_besser/gesamt*100:.1f}%)")
col4.metric('⬇️ Wechsel schlechter',  f"{anzahl_schlechter} ({anzahl_schlechter/gesamt*100:.1f}%)")

st.markdown('---')


# PLOT 1
st.subheader('📊 Rating-Verteilung: Alle Bücher vs. Genre-Wechsel')
st.image('src/figures/plot1_rating_uebersicht.png')
st.markdown("""
> Histogramm aller Bewertungen, nur Genrewechsel Bücher, und Boxplot-Vergleich nebeneinander.
> Der Boxplot zeigt, dass Hauptgenre und Genrewechsel Bücher haben eine sehr ähnliche Bewertungsverteilung.
""")
st.markdown('---')


# PLOT 2
st.subheader('📈 Erfolg des Genre-Wechsels')
st.image('src/figures/plot2_differenz_uebersicht.png')
st.markdown(f"""
> Das Histogramm zeigt die Differenz pro Autor.
> Die rote Linie ist der Nullpunkt und  rechts davon war der Wechsel besser.
> Durchschnittliche Differenz: **{results['Differenz'].mean():+.3f}**
""")
st.markdown('---')


# PLOT 3
st.subheader('🔍 Hauptgenre vs. Genre-Wechsel Rating pro Autor')
st.image('src/figures/plot3_scatter_autoren.png')
st.markdown("""
> Jeder Punkt ist ein Autor. Punkte oberhalb der grauen Diagonale bedeutet, dass der Genrewechsel besser bewertet wurde.
> Die Punkte verteilen sich relativ gleichmäßig um die Linie.
""")
st.markdown('---')


# PLOT 4 + 5 nebeneinander
st.subheader('🏆 Top Autoren und die häufigste Genrewechsel Kombinationen')
col_l, col_r = st.columns(2)

with col_l:
    st.image('src/figures/plot4_top_wechsler.png')
    st.markdown('> Die 10 Autoren mit den meisten Genrewechsel Büchern.')

with col_r:
    st.image('src/figures/plot5_top_kombinationen.png')
    st.markdown('> Die 10 häufigsten Genrewechsel Kombinationen (Von → Nach).')

st.markdown('---')

# ROHDATEN
tab1, tab2 = st.tabs(['📋 Rohdaten', '📊 Ergebnisse pro Autor'])

with tab1:
    st.dataframe(df.head(50))

with tab2:
    st.dataframe(results.sort_values('Differenz', ascending=False))