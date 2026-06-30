import pandas as pd
import os
import matplotlib.pyplot as plt


df_clean = pd.read_csv('GoodReads_clean.csv')
pd.set_option('display.float_format', '{:.2f}'.format) # 2 Nachkommastellen
print(f"Starte Analyse mit {df_clean.shape[0]} Zeilen\n")

def extrahiere_erstes_genre(genre_text):
    return genre_text.split(',')[0]

def finde_haeufigstes_genre(genres_des_autors):
    return genres_des_autors.value_counts().idxmax()

# Spalten für die Analyse vorbereiten
df_clean['buch_genre'] = df_clean['genre'].apply(extrahiere_erstes_genre)

stammgenre_verzeichnis = df_clean.groupby('author')['buch_genre'].agg(finde_haeufigstes_genre)
df_clean['stammgenre_autor'] = df_clean['author'].map(stammgenre_verzeichnis)
df_clean['ist_genrewechsel']  = df_clean['buch_genre'] != df_clean['stammgenre_autor']

# Hilfsfunktion für den Überblick pro Autor
def zaehle_stammgenre_buecher(buecher_status):
    return (buecher_status == False).sum()

autoren_uebersicht = df_clean.groupby('author').agg(
    gesamt_buecher          = ('title', 'count'),
    hauptgenre              = ('stammgenre_autor', 'first'),
    anzahl_stammgenre_buecher = ('ist_genrewechsel', zaehle_stammgenre_buecher),
    anzahl_wechsel_buecher    = ('ist_genrewechsel', 'sum'),
).reset_index()

print("Top 15 Autoren nach Buchanzahl")
print(autoren_uebersicht.sort_values('gesamt_buecher', ascending=False).head(15).to_string(index=False))

# Nur Autoren mit mind. einem Genrewechsel filtern
autoren_mit_wechsel = autoren_uebersicht[autoren_uebersicht['anzahl_wechsel_buecher'] >= 1]['author']
df_wechsel_autoren = df_clean[df_clean['author'].isin(autoren_mit_wechsel)]

print(f"\nAutoren mit mind. 1 Genre-Wechsel: {len(autoren_mit_wechsel)}")

# Durchschnitts-Rating Hauptgenre und Genrewechsel pro Autor
rating_stammgenre = df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == False].groupby('author')['rating'].mean()
rating_wechsel    = df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == True].groupby('author')['rating'].mean()

bewertungs_vergleich = pd.DataFrame({
    'durchschnitt_stammgenre': rating_stammgenre,
    'durchschnitt_wechsel':    rating_wechsel
})

bewertungs_vergleich['differenz'] = bewertungs_vergleich['durchschnitt_wechsel'] - bewertungs_vergleich['durchschnitt_stammgenre']

print("BEWERTUNGSVERGLEICH PRO AUTOR")
print(bewertungs_vergleich.sort_values('differenz', ascending=False).to_string())

# Gesamtergebnis auswerten
anzahl_besser     = (bewertungs_vergleich['differenz'] > 0).sum()
anzahl_schlechter = (bewertungs_vergleich['differenz'] < 0).sum()
gesamt_anzahl     = len(bewertungs_vergleich)

print("\nERGEBNIS")
print(f"Wechsel besser bewertet:     {anzahl_besser}  ({anzahl_besser / gesamt_anzahl * 100:.1f}%)")
print(f"Wechsel schlechter bewertet: {anzahl_schlechter} ({anzahl_schlechter / gesamt_anzahl * 100:.1f}%)")
print(f"Durchschnittliche Differenz: {bewertungs_vergleich['differenz'].mean():+.3f}")

# Auf welche Genres wurde gewechselt?
print("\nGENREWECHSEL VON NACH")

alle_wechsel_buecher = df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == True].copy()

wechsel_kombinationen = alle_wechsel_buecher.groupby(['stammgenre_autor', 'buch_genre']).agg(
    anzahl_buecher = ('rating', 'count'),
    avg_rating     = ('rating', 'mean')
).reset_index()

wechsel_kombinationen.columns = ['von_hauptgenre', 'gewechselt_zu', 'anzahl_buecher', 'durchschnitts_rating']
wechsel_kombinationen = wechsel_kombinationen[wechsel_kombinationen['von_hauptgenre'] != wechsel_kombinationen['gewechselt_zu']]
wechsel_kombinationen = wechsel_kombinationen.sort_values('anzahl_buecher', ascending=False)

print(wechsel_kombinationen.head(20).to_string(index=False))

df_clean.to_csv("genre_switch_results.csv", index=False)

# VISUALISIERUNG
os.makedirs("figures", exist_ok=True)

# Rating-Verteilung (alle Bücher + nur Wechsel Bücher + Boxplot
fig, ax = plt.subplots(1, 3, figsize=(16, 5))

# Alle Ratings
ax[0].hist(df_clean['rating'], bins=30, edgecolor='black', color='steelblue')
ax[0].set_xlabel('Rating')
ax[0].set_title('Alle Ratings')

# Nur Genre-Wechsel Bücher
wechsel_ratings = df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == True]['rating']
ax[1].hist(wechsel_ratings, bins=30, color='orange', edgecolor='black')
ax[1].set_xlabel('Rating')
ax[1].set_title('Ratings Genrewechsel Bücher')

# Boxplot
ax[2].boxplot([
    df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == False]['rating'],
    df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == True]['rating']
], labels=['Hauptgenre', 'Genre-Wechsel'])
ax[2].set_ylabel('Rating')
ax[2].set_title('Boxplot Vergleich')

plt.tight_layout()
fig.savefig("figures/plot1_rating_uebersicht.png", dpi=300, bbox_inches="tight")
plt.show()

print(f"Ø Rating Hauptgenre:    {df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == False]['rating'].mean():.2f}")
print(f"Ø Rating Genre-Wechsel: {df_wechsel_autoren[df_wechsel_autoren['ist_genrewechsel'] == True]['rating'].mean():.2f}")


#Anteil Wechsel besser vs. schlechter
fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# Histogramm der Differenzen
ax[0].hist(bewertungs_vergleich['differenz'], bins=30, color='purple', edgecolor='black')
ax[0].axvline(0, color='red', linestyle='--', linewidth=1.5)
ax[0].set_xlabel('Differenz (Genrewechsel - Hauptgenre)')
ax[0].set_title('Erfolg vom Genrewechsel')

# Pie Chart
besser    = (bewertungs_vergleich['differenz'] > 0).sum()
schlechter = (bewertungs_vergleich['differenz'] < 0).sum()
ax[1].pie(
    [besser, schlechter],
    labels=['Wechsel besser', 'Wechsel schlechter'],
    autopct='%1.1f%%',
    colors=['#2a78d6', '#e34948']
)
ax[1].set_title('Wechsel besser oder schlechter bewertet?')

plt.tight_layout()
fig.savefig("figures/plot2_differenz_uebersicht.png", dpi=300, bbox_inches="tight")
plt.show()


# Hauptgenre vs. Wechselgenre Rating pro Autor
bv = bewertungs_vergleich.reset_index()

plt.figure(figsize=(10, 6))
plt.scatter(bv['durchschnitt_stammgenre'], bv['durchschnitt_wechsel'], alpha=0.4)
plt.plot([3, 5], [3, 5], color='gray', linestyle='--', linewidth=1)  # Diagonale
plt.xlabel('Ø Rating Hauptgenre')
plt.ylabel('Ø Rating Genrewechsel')
plt.title('Hauptgenre vs. Genrewechsel Bewertung pro Autor')
plt.tight_layout()
plt.savefig("figures/plot3_scatter_autoren.png", dpi=300, bbox_inches="tight")
plt.show()

corr = bv['durchschnitt_stammgenre'].corr(bv['durchschnitt_wechsel'])
print(f"Korrelation: {corr:.3f}")


# Top 10 Autoren mit den meisten Genrewechseln
top_wechsler = autoren_uebersicht.sort_values('anzahl_wechsel_buecher', ascending=False).head(10)

plt.figure(figsize=(12, 6))
plt.barh(range(len(top_wechsler)), top_wechsler['anzahl_wechsel_buecher'], color='teal')
plt.yticks(range(len(top_wechsler)), top_wechsler['author'])
plt.xlabel('Anzahl Genrewechsel Bücher')
plt.title('Top 10 Autoren mit den meisten Genrewechseln')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("figures/plot4_top_wechsler.png", dpi=300, bbox_inches="tight")
plt.show()


# Top 10 häufigste Genrewechsel Kombinationen
top_kombis = wechsel_kombinationen.head(10).copy()
top_kombis['label'] = top_kombis['von_hauptgenre'] + ' → ' + top_kombis['gewechselt_zu']

plt.figure(figsize=(12, 6))
plt.barh(range(len(top_kombis)), top_kombis['anzahl_buecher'], color='coral')
plt.yticks(range(len(top_kombis)), top_kombis['label'])
plt.xlabel('Anzahl der wechsel Bücher')
plt.title('Top 10 häufigste Genre-Wechsel (Von → Nach)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("figures/plot5_top_kombinationen.png", dpi=300, bbox_inches="tight")
plt.show()

print(top_kombis[['label', 'anzahl_buecher', 'durchschnitts_rating']].to_string(index=False))
