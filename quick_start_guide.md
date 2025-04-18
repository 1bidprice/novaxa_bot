# NOVAXA Quick Start Guide

Αυτός ο οδηγός γρήγορης εκκίνησης θα σας βοηθήσει να ξεκινήσετε άμεσα με το NOVAXA Telegram bot και το web dashboard σας.

## 1. Πρόσβαση στο Telegram Bot

1. Ανοίξτε το Telegram στο κινητό ή τον υπολογιστή σας
2. Αναζητήστε το bot σας με το όνομα χρήστη `@NOVAXA_Bot` (ή το όνομα που επιλέξατε)
3. Πατήστε "Start" ή στείλτε την εντολή `/start`
4. Το bot θα σας καλωσορίσει και θα σας παρουσιάσει τις διαθέσιμες εντολές

## 2. Βασικές Εντολές του Bot

- `/start` - Εκκίνηση του bot και εμφάνιση του μενού βοήθειας
- `/help` - Εμφάνιση όλων των διαθέσιμων εντολών
- `/stocks` - Προβολή των τρεχουσών τιμών των μετοχών (ΟΠΑΠ, METLEN)
- `/bidprice` - Προβολή της κατάστασης του project BidPrice
- `/amesis` - Προβολή της κατάστασης του project Amesis
- `/6225` - Προβολή της κατάστασης του project 6225
- `/progress` - Προβολή της συνολικής προόδου όλων των projects
- `/status` - Έλεγχος της κατάστασης του bot και των συνδεδεμένων υπηρεσιών
- `/logs` - Προβολή των πρόσφατων καταγραφών συμβάντων
- `/broadcast` - Αποστολή μαζικού μηνύματος (μόνο για διαχειριστές)

## 3. Πρόσβαση στο Web Dashboard

1. Ανοίξτε το πρόγραμμα περιήγησης και επισκεφθείτε τη διεύθυνση:
   https://novaxa-dashboard.onrender.com

2. Το dashboard θα φορτώσει αυτόματα και θα εμφανίσει:
   - Τις τρέχουσες τιμές των μετοχών
   - Την κατάσταση των projects
   - Τις πρόσφατες ειδοποιήσεις
   - Την καθημερινή πρόοδο

3. Χρησιμοποιήστε το μενού στα αριστερά για να περιηγηθείτε στις διάφορες ενότητες

## 4. Παρακολούθηση Μετοχών

### Στο Telegram Bot:
1. Στείλτε την εντολή `/stocks` για να δείτε τις τρέχουσες τιμές
2. Χρησιμοποιήστε `/stock ΟΠΑΠ` ή `/stock METLEN` για συγκεκριμένες μετοχές
3. Ορίστε ειδοποιήσεις με την εντολή `/setalert ΟΠΑΠ 18.50`

### Στο Web Dashboard:
1. Πλοηγηθείτε στην ενότητα "Μετοχές" από το μενού
2. Δείτε αναλυτικές πληροφορίες για κάθε μετοχή
3. Προσθέστε νέες μετοχές με το κουμπί "Προσθήκη Μετοχής"
4. Ορίστε όρια ειδοποιήσεων με το κουμπί "Επεξεργασία" στην κάρτα κάθε μετοχής

## 5. Διαχείριση Projects

### Στο Telegram Bot:
1. Χρησιμοποιήστε τις εντολές `/bidprice`, `/amesis`, ή `/6225` για να δείτε την κατάσταση κάθε project
2. Στείλτε `/progress` για να δείτε τη συνολική πρόοδο
3. Χρησιμοποιήστε `/logs project_name` για να δείτε τα logs συγκεκριμένου project

### Στο Web Dashboard:
1. Πλοηγηθείτε στην ενότητα "Projects" από το μενού
2. Δείτε αναλυτικές πληροφορίες για κάθε project
3. Πατήστε "Προβολή Logs" για να δείτε τα πρόσφατα logs
4. Πατήστε "Λεπτομέρειες" για περισσότερες πληροφορίες

## 6. Ειδοποιήσεις και Alerts

- Το bot θα σας στέλνει αυτόματα ειδοποιήσεις όταν:
  - Οι τιμές των μετοχών φτάσουν στα όρια που έχετε ορίσει
  - Υπάρχουν σημαντικές αλλαγές στα projects
  - Προκύψουν σφάλματα ή προβλήματα στο σύστημα

- Στο Web Dashboard, μπορείτε να δείτε όλες τις ειδοποιήσεις στην ενότητα "Ειδοποιήσεις"

## 7. Ενημέρωση του Bot Token

Αν χρειαστεί να ενημερώσετε το token του bot:

1. Επισκεφθείτε το Render Dashboard: https://dashboard.render.com/
2. Επιλέξτε και τις δύο υπηρεσίες (`novaxa-telegram-bot` και `novaxa-dashboard`)
3. Πηγαίνετε στην καρτέλα "Environment"
4. Ενημερώστε τη μεταβλητή `BOT_TOKEN` και στις δύο υπηρεσίες
5. Πατήστε "Save Changes"

Εναλλακτικά, μπορείτε να ενημερώσετε το token από το Web Dashboard:
1. Πλοηγηθείτε στην ενότητα "Ρυθμίσεις"
2. Βρείτε την ενότητα "Telegram Bot"
3. Πατήστε "Ενημέρωση" δίπλα στο Bot Token
4. Εισάγετε το νέο token και πατήστε "Ενημέρωση"

## 8. Αντιμετώπιση Προβλημάτων

Αν αντιμετωπίσετε προβλήματα:

1. Ελέγξτε αν το bot ανταποκρίνεται με την εντολή `/status`
2. Επισκεφθείτε το Render Dashboard και ελέγξτε τα logs των υπηρεσιών
3. Εκτελέστε το script δοκιμής για διάγνωση προβλημάτων:
   ```
   python3 test_deployment.py
   ```
4. Βεβαιωθείτε ότι το token του bot είναι έγκυρο και ενημερωμένο

## 9. Επόμενα Βήματα

- Εξερευνήστε όλες τις λειτουργίες του bot και του dashboard
- Προσαρμόστε τις ρυθμίσεις ειδοποιήσεων στις ανάγκες σας
- Ρυθμίστε τα όρια για τις τιμές των μετοχών
- Εξετάστε την προσθήκη επιπλέον μετοχών για παρακολούθηση

## 10. Υποστήριξη

Για περισσότερες πληροφορίες και λεπτομερείς οδηγίες, ανατρέξτε στα ακόλουθα αρχεία:

- `documentation.md` - Πλήρης τεκμηρίωση του συστήματος
- `render_deployment_guide.md` - Οδηγός ανάπτυξης στο Render
- `continuous_deployment.md` - Πληροφορίες για συνεχή ανάπτυξη και παρακολούθηση
- `access_credentials.md` - Διαπιστευτήρια πρόσβασης και πληροφορίες ασφαλείας
