#Datei einlesen
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
print("Bibliotheken importiert")

df = pd.read_csv('/Users/milenka/Desktop/PycharmProjects/PythonProject1/data/GoodReads_100k_books.csv')
df_clean = df.copy()
print(f"Geladen: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")

#Ueberblick über die Daten
important = ['author', 'title', 'genre', 'rating', 'reviews', 'totalratings']

#Tabellenansicht
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\nWichtige Spalten:")
print(df[important].head())
print("\nBewertungen-Beispiele:")
print(df['rating'].head(5))

#Unlesbare Daten
broken_titles = df[
    df['title'].astype(str).str.contains(r'[ÙØÂ�]', regex=True)
]

broken_author = df[
    df['author'].astype(str).str.contains(r'[ÙØÂ�]', regex=True)
]

#Daten bestehen nur aus zahlen
numbered_title = df[
    df['title'].astype(str).str.fullmatch(r'[\d\s\W]+')
]

numbered_author = df[
    df['author'].astype(str).str.fullmatch(r'[\d\s\W]+')
]

# Vorher
before_cleaning = df_clean.shape[0]
print(f"Vor den löschen der unlesbaren daten: {before_cleaning} Zeilen")

df_clean = df_clean.drop(index=broken_titles.index, errors='ignore')
df_clean = df_clean.drop(index=broken_author.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_title.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_author.index, errors='ignore')

after_cleaning =  df_clean.shape[0]
print(f"{after_cleaning - before_cleaning} Zeilen")
print(f"  davon unleserliche Titel: {len(broken_titles)}")
print(f"  davon unleserliche Autoren: {len(broken_author)}")
print(f"  davon Zahlen-Titel: {len(numbered_title)}")
print(f"  davon Zahlen-Autoren: {len(numbered_author)}")

#Fehlende Werte identifizieren
missing = df_clean[important].isnull().sum()
missing_pct = (missing / len(df_clean)) * 100
missing_df = pd.DataFrame({
    'Spalte': missing.index,
    'Fehlend': missing.values,
    'Prozent': missing_pct.values
})

missing_df = missing_df[missing_df['Fehlend'] > 0]
print(missing_df)

before = df_clean.shape[0]

df_clean = df_clean.dropna(subset=['title'])
df_clean = df_clean.dropna(subset=['genre'])

after = df_clean.shape[0]
print(f"Gelöscht: {before - after} fehlenden Werte")

#Duplikate
dups = df_clean.duplicated(subset=['isbn']).sum()
print(f"Duplikate: {dups}")
df_clean.drop_duplicates(subset=['isbn'], inplace=True)
print(f"Nach Entfernung der Duplikate: {df_clean.shape[0]} Zeilen")

# Ausreißer behandeln
df_clean = df_clean[df_clean['rating'] > 0]
df_clean = df_clean[df_clean['rating'] <= 5]
print(f"Nach Rating-Bereinigung: {df_clean.shape[0]} Zeilen")

# Ausreißer mit IQR
for col in ['reviews', 'totalratings']:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)]
    print(f"{col}: {len(outliers)} Ausreißer behalten, da populäre Bücher realistisch hohe und viele Bewertungen haben")

# Ausreißer entfernen rating unter/gleich 0 und über 5
lower_bound = 0
upper_bound = 5

df_clean = df_clean[(df_clean['rating'] > lower_bound) & (df_clean['rating'] <= upper_bound)]
print(f"Nach Rating-Bereinigung: {df_clean.shape[0]} Zeilen")

# Rating Statistiken und Visualisierung
print("Rating-Statistiken:")
print(df_clean['rating'].describe())

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

#rating mit = 0
axes[0].boxplot(df['rating'].dropna())
axes[0].set_title('Ratings inkl. 0')
axes[0].set_ylim(-0.5, 5.5)

#bereinigt
axes[1].boxplot(df_clean['rating'].dropna())
axes[1].set_title('Ratings ohne 0')
axes[1].set_ylim(-0.5, 5.5)

plt.show()

categorical_cols = ['author', 'genre', 'title']

for col in categorical_cols:
    print(f"\n{col}:")
    print(df_clean[col].value_counts().head(5))

# Inkonsistenzen beheben
df_clean['author'] = df_clean['author'].str.strip().str.title()
df_clean['genre'] = df_clean['genre'].str.strip().str.title()

print("\nNach Bereinigung:")
print(df_clean[['author', 'genre', 'title']].head())