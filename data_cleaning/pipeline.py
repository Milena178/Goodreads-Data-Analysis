#Datei einlesen
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)
print("Bibliotheken importiert")

df = pd.read_csv('../data/GoodReads_100k_books.csv')
df_clean = df.copy()
print(f"Geladen: {df.shape[0]} Zeilen, {df.shape[1]} Spalten")

#Ueberblick über die Daten
important = ['author', 'title', 'genre', 'rating', 'isbn', 'totalratings']

#Tabellenansicht
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\nWichtige Spalten:")
print(df[important].head())
print("\nBewertungen-Beispiele:")
print(df['rating'].head(5))

# Nicht relevante Spalten entfernen
df_clean = df_clean[['author', 'title', 'genre', 'rating', 'isbn', 'totalratings']]
print(f"Spalten nach entfernung: {df_clean.columns.tolist()}")

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
before = df_clean.shape[0]

df_clean = df_clean.drop(index=broken_titles.index, errors='ignore')
df_clean = df_clean.drop(index=broken_author.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_title.index, errors='ignore')
df_clean = df_clean.drop(index=numbered_author.index, errors='ignore')

print(f"Vorher: {before} Zeilen")
print(f"Nachher: {df_clean.shape[0]} Zeilen")
print(f"Gelöscht: {before - df_clean.shape[0]} Zeilen")

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

df_clean = df_clean.dropna(subset=['title'])
df_clean = df_clean.dropna(subset=['genre'])
df_clean = df_clean.dropna(subset=['isbn'])

print(f"{df_clean.shape[0]} Zeilen")

#Duplikate
dups = df_clean.duplicated(subset=['isbn']).sum()
print(f"Duplikate: {dups}")
df_clean.drop_duplicates(subset=['isbn'], inplace=True)

# Ausreißer mit IQR
for col in ['rating', 'totalratings']:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df_clean[(df_clean[col] < lower_bound) | (df_clean[col] > upper_bound)]
    print(f"{col}: {len(outliers)}")

# Ausreißer entfernen rating unter/gleich 0 und über 5
lower_bound = 0
upper_bound = 5

df_clean = df_clean[(df_clean['rating'] > lower_bound) & (df_clean['rating'] <= upper_bound)]

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

plt.savefig('rating_boxplot.png', dpi=150, bbox_inches='tight')
plt.show()

# Inkonsistenzen beheben
categorical_cols = ['author', 'title']

for col in categorical_cols:
    print(f"\n{col}:")
    print(df_clean[col].value_counts().head(5))

df_clean['author'] = df_clean['author'].str.strip().str.title()
df_clean['title'] = df_clean['title'].str.strip()

# Finale Überprüfung
print("Finale Dimensionen:")
print(df_clean.shape)

print("\nFehlende Werte:")
print(df_clean.isnull().sum())

print("\nDatentypen:")
print(df_clean.dtypes)

print("\nErste Zeilen des bereinigten Datensatzes:")
print(df_clean.head())

#Speichern
df_clean.to_csv('GoodReads_clean.csv', index=False)
print("Bereinigter Datensatz wurde gespeichert!")
