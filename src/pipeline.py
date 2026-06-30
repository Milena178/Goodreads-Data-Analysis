#Datei einlesen
import pandas as pd

print("Bibliotheken importiert")

df = pd.read_csv('../data/GoodReads_100k_books.csv')
df_clean = df.copy()
print(f"Geladen: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")

#Ueberblick über die Daten
important = ['author', 'title', 'genre', 'rating', 'isbn', 'isbn13', 'totalratings']

#Tabellenansicht
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("Shape:", df.shape)
print("\nWichtige Spalten:")
print(df[important].head())
print("\nGenre-Beispiele:")
print(df['genre'].head(5))

# NICHT RELEVANTE SPALTEN ENTFERNEN
df_clean = df_clean[['author', 'title', 'genre', 'rating', 'isbn', 'isbn13', 'totalratings']]
print(f"Spalten nach entfernung: {df_clean.columns.tolist()}")

#DATENTYPEN UEBEPRUFEN
print(f"Datentypen überfprüfen:")
print(f"Author: {df['author'].dtype}")
print(f"Titel: {df['title'].dtype}")
print(f"Genre: {df['genre'].dtype}")
print(f"Rating: {df['rating'].dtype}")
print(f"ISBN: {df['isbn'].dtype}")
print(f"ISBN13: {df['isbn13'].dtype}")
print(f"Totalratings: {df['totalratings'].dtype}")

#UNLESBARE DATEN (kaputte Zeichen)
broken_titles = df[
    df['title'].str.contains(r'[ÙØÂ�]', regex=True)
]

broken_author = df[
    df['author'].str.contains(r'[ÙØÂ�]', regex=True)
]

#DATEN DIE NUR AUS ZAHLEN BESTEHEN
numbered_title = df[
    df['title'].str.fullmatch(r'[\d\s\W]+')
]

numbered_author = df[
    df['author'].str.fullmatch(r'[\d\s\W]+')
]

#Vor dem loeschen der unlesbaren Daten
before = df_clean.shape[0]

df_clean = df_clean.drop(index=broken_titles.index, errors='ignore')
df_clean = df_clean.drop(index=broken_author.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_title.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_author.index, errors='ignore')

print(f"Beispiel: {(broken_titles[['title', 'author']].head(3))}")

print(f"Vorher: {before} Zeilen")
print(f"Nachher: {df_clean.shape[0]} Zeilen")
print(f"Gelöscht: {before - df_clean.shape[0]} Zeilen")

#FEHLENDE WERTEN
missing = df_clean[important].isnull().sum()
missing_pct = (missing / len(df_clean)) * 100
missing_df = pd.DataFrame({
    'Spalte': missing.index,
    'Fehlend': missing.values,
    'Prozent': missing_pct.values
})

missing_df = missing_df[missing_df['Fehlend'] > 0]
print(missing_df)

df_clean = df_clean.dropna(subset=['title', 'genre'])

print(f"{df_clean.shape[0]} Zeilen nach dem löschen der fehlenden Werten")

#DUPLIKATE
dups = df_clean.duplicated(subset=['isbn', 'isbn13']).sum()
print(f"Duplikate: {dups}")
df_clean.drop_duplicates(subset=['isbn', 'isbn13'], inplace=True)
print(f"Nach Entfernung: {df_clean.shape[0]} Zeilen")

#Begrenzung der Bewertungen zwischen 0 und 5
rating_low = 1
rating_high = 5

#Bewertungen 0 und über 5 und weniger als 10 Bewertungen löschen
df_clean = df_clean[(df_clean['rating'] >= rating_low) & (df_clean['rating'] <= rating_high) & (df_clean['totalratings'] >= 10)]
print(f"Nach Entfernung von Bewertungen unter 1 und über 5 : {df_clean.shape[0]} Zeilen")

# Autoren mit weniger als 5 Büchern rausfiltern
author_counts = df_clean['author'].value_counts()
df_clean = df_clean[df_clean['author'].isin(author_counts[author_counts >= 5].index)]
print(f"Nach Autor-Filter (mind. 5 Bücher): {df_clean.shape[0]} Zeilen\n")

#INKONSISTENZ BEHEBEN
categorical_cols = ['author', 'title']

for col in categorical_cols:
    print(df_clean[col].value_counts().head(5))

df_clean['author'] = df_clean['author'].str.strip().str.title()
df_clean['title'] = df_clean['title'].str.strip()
df_clean['genre'] = df_clean['genre'].str.strip()

# Finale Überprüfung
print("Finale Dimensionen:")
print(df_clean.shape)

print("\nFehlende Werte:")
print(df_clean.isnull().sum())

print("\nDatentypen:")
print(df_clean.dtypes)

print("\nErste Zeilen des bereinigten Datensatzes:")
print(df_clean.head())

df_clean.to_csv('GoodReads_clean.csv', index=False)
print("Bereinigter Datensatz wurde gespeichert!")
