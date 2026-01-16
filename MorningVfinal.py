# app.py
import streamlit as st
import json
from collections import defaultdict
import streamlit.components.v1 as components

st.set_page_config(page_title="Générateur d'agenda (sidebar avec copy)", layout="wide")
st.title("Générateur d'agenda pour la morning call (9:15am Paris)")

teams_link = (
    "https://teams.microsoft.com/l/meetup-join/19%3ameeting_OGVlMmM1MTMtNDA4Ni00ZjE0LTk3ZWUtNDI4NzM3MTg2MTFj%40thread.v2/0"
    "?context=%7b%22Tid%22%3a%22a5c34232-eadc-4609-bff3-dd6fcdae3fe2%22%2c%22Oid%22%3a%22340d7b0d-8d5c-4913-9cf0-8f57286f28ce%22%7d"
)

analysts = [
    "Amarkhodja Amine",
    "Baudet François",
    "Bourgoin Arnaud",
    "Conlon Paul",
    "Courtiade Laure",
    "Dedise Sophie",
    "Jaeger Robert",
    "Jeanniard Rémi",
    "Klein Pierre Andre",
    "Le Bihan Pierre",
    "Shnaps David",
    "Taillepied Stéphane",
    "Teissier Jean-baptiste",
]

# Sidebar : selection des intervenants
st.sidebar.header("Choix des intervenants")
selected = st.sidebar.multiselect("Sélectionne les analystes qui vont parler :", options=analysts, default=[])

st.sidebar.markdown("---")
st.sidebar.markdown("Quand tu as sélectionné les analystes qui vont intervenir, remplis leurs informations sur la page principale.")

st.markdown(
    "Dans la page principale : choisis pour chaque intervenant s'il s'agit de IG/HY/Autre (label perso) et renseigne le sujet. "
)

if not selected:
    st.info("Aucun intervenant sélectionné. Va dans la sidebar pour choisir les analystes qui vont parler.")
else:
    # Afficher les contrôles pour chaque intervenant sélectionné
    choices = []
    for i, name in enumerate(selected):
        cols = st.columns([3, 1.2, 4, 3])
        cols[0].markdown(f"**{name}**")
        opts = ["IG", "HY", "Autre..."]
        sel = cols[1].selectbox("", opts, index=0, key=f"sel_{i}")
        custom_group = ""
        if sel == "Autre...":
            custom_group = cols[2].text_input("Label du groupe", value="", placeholder="Ex: EM, Sovs...", key=f"custom_group_{i}")
            topic = cols[3].text_input("Sujet", value="", placeholder="Ex: BMW", key=f"topic_{i}")
        else:
            topic = cols[2].text_input("Sujet", value="", placeholder="Ex: BMW", key=f"topic_{i}")
        choices.append({
            "name": name,
            "sel": sel,
            "custom_group": custom_group.strip(),
            "topic": topic.strip()
        })

    # Bouton de génération
    if st.button("Générer le message"):
        final = []
        for c in choices:
            name = c["name"]
            # déterminer le label de groupe
            if c["sel"] == "IG":
                group_label = "IG"
            elif c["sel"] == "HY":
                group_label = "HY"
            else:
                group_label = c["custom_group"] if c["custom_group"] else "Other"
            topic = c["topic"] if c["topic"] else ""
            final.append((group_label, name, topic))

        if not final:
            st.warning("Les intervenants sont sélectionnés mais aucun sujet renseigné. Renseigne au moins un sujet.")
        else:
            # Regrouper par label (IG et HY en priorité, puis les autres par ordre alphabétique)
            groups = defaultdict(list)
            for g, n, t in final:
                groups[g].append((n, t))

            ordered_group_labels = []
            if "IG" in groups:
                ordered_group_labels.append("IG")
            if "HY" in groups:
                ordered_group_labels.append("HY")
            other_labels = sorted([lbl for lbl in groups.keys() if lbl not in ("IG", "HY")])
            ordered_group_labels.extend(other_labels)

            parts = []
            parts.append("Good morning everyone, here is today's agenda for our morning call scheduled at 9:15am (Paris time). Below the link to join the meeting :\n")
            for lbl in ordered_group_labels:
                parts.append(lbl)
                for name, topic in groups[lbl]:
                    parts.append(f"{topic} - {name}")
                parts.append("")  # ligne vide entre groupes

            parts.append(f"Link ->{teams_link}")
            parts.append("Join conversation")

            message = "\n".join(parts)

            st.subheader("Message généré (copier/coller)")
            st.text_area("Message", value=message, height=320)

            # Bouton Copier via composant HTML/JS
            safe_message_json = json.dumps(message)  # échappe correctement les quotes et sauts de ligne
            html = f"""
            <div>
              <button id="copy-btn" style="padding:6px 12px; font-size:14px;">Copier le message</button>
              <span id="copy-status" style="margin-left:10px;color:green;"></span>
            </div>
            <script>
            const msg = {safe_message_json};
            const btn = document.getElementById("copy-btn");
            const status = document.getElementById("copy-status");
            btn.addEventListener("click", async () => {{
                try {{
                    await navigator.clipboard.writeText(msg);
                    status.textContent = "Copié !";
                    setTimeout(() => status.textContent = "", 2000);
                }} catch (err) {{
                    // fallback pour anciens navigateurs
                    const ta = document.createElement('textarea');
                    ta.value = msg;
                    document.body.appendChild(ta);
                    ta.select();
                    try {{
                        document.execCommand('copy');
                        status.textContent = "Copié !";
                        setTimeout(() => status.textContent = "", 2000);
                    }} catch (e) {{
                        alert('Échec du copier dans le presse-papiers : ' + e);
                    }}
                    document.body.removeChild(ta);
                }}
            }});
            </script>
            """
            components.html(html, height=60)
    else:
        st.info("Remplis les champs pour les intervenants sélectionnés puis clique sur 'Générer le message'.")
