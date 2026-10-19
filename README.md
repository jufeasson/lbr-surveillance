# Surveillance extérieure Le Bouton Rouge

Petit moniteur indépendant de l’hébergement du site. Ce dépôt contient seulement le code de sondes et des URL publiques : aucun code métier LBR, secret, donnée client, accès administrateur ou clé de sauvegarde.

GitHub Actions exécute trois essais bornés de l’accueil HTTPS et de l’état technique public, environ toutes les quinze minutes. Après 06 h Paris, à partir du 20 octobre 2026, il contrôle aussi une sauvegarde vérifiée démarrée dans la fenêtre nocturne attendue. Aucun paiement, rendez-vous, email client ou écriture sur le site. Vérification TLS normale, redirections refusées, réponses bornées et non publiées dans les logs.

Les échecs utilisent les notifications natives GitHub du propriétaire qui a créé la planification. Leur destination et leur réception doivent être vérifiées dans le compte avant de déclarer les alertes opérationnelles. Le lancement manuel « exercise » produit un échec explicitement fictif, sans modifier le site.

Activation du 19 octobre 2026 : [sonde manuelle réussie](https://github.com/jufeasson/lbr-surveillance/actions/runs/39235452256), [alerte fictive](https://github.com/jufeasson/lbr-surveillance/actions/runs/39235456822) réellement reçue à12h10min38Paris, puis [contrôle sain](https://github.com/jufeasson/lbr-surveillance/actions/runs/39235711568). Ce sont des lancements manuels ; le premier passage `schedule` et la première sauvegarde nocturne restent des preuves distinctes à relever.

Les exécutions sur runners standard dans un dépôt public sont [gratuites selon GitHub](https://docs.github.com/en/actions/concepts/billing-and-usage). Aucun service payant ni secret d’envoi n’est utilisé. Le site et son dépôt métier restent distincts.

## Limites et entretien

La cadence est indicative : GitHub peut retarder ou omettre des déclenchements sous forte charge. Les planifications publiques sont désactivées après soixante jours sans activité du dépôt ; contrôler régulièrement leur état et les réactiver si nécessaire. [Règles officielles](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). Ce n’est pas un engagement de disponibilité ou de délai d’alerte. Les notifications dépendent aussi du compte GitHub et de sa messagerie ; une panne de GitHub n’est pas détectée par ce moniteur lui-même.

Les logs et résultats de sondes sont publics. Ils ne contiennent que des états techniques d’URL déjà publiques. Le seed manuel du 19 octobre ne satisfait pas la sonde nocturne. Une exécution vérifiée dans la fenêtre attendue n’authentifie pas à elle seule l’origine cron du lancement : le premier passage réel doit être observé séparément.
