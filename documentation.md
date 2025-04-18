# NOVAXA Dashboard και Telegram Bot - Οδηγίες Χρήσης

## Εισαγωγή

Το NOVAXA είναι ένα ολοκληρωμένο σύστημα που αποτελείται από ένα επαγγελματικό Telegram bot και ένα web dashboard. Σχεδιάστηκε για να σας βοηθήσει να παρακολουθείτε τις μετοχές του Χρηματιστηρίου Αθηνών, να διαχειρίζεστε τα projects σας (BidPrice, Amesis, Project6225) και να λαμβάνετε αυτοματοποιημένες ειδοποιήσεις.

## Περιεχόμενα

1. [Εγκατάσταση και Ανάπτυξη](#εγκατάσταση-και-ανάπτυξη)
2. [Telegram Bot](#telegram-bot)
3. [Web Dashboard](#web-dashboard)
4. [Παρακολούθηση Μετοχών](#παρακολούθηση-μετοχών)
5. [Διαχείριση Projects](#διαχείριση-projects)
6. [Ειδοποιήσεις και Alerts](#ειδοποιήσεις-και-alerts)
7. [Συντήρηση και Αναβαθμίσεις](#συντήρηση-και-αναβαθμίσεις)

## Εγκατάσταση και Ανάπτυξη

### Προαπαιτούμενα

- Docker και Docker Compose
- Python 3.10 ή νεότερη έκδοση
- Πρόσβαση στο Telegram Bot API (το token έχει ήδη ρυθμιστεί)

### Βήματα Εγκατάστασης

1. Κλωνοποιήστε το repository:
   ```
   git clone https://github.com/yourusername/novaxa-dashboard.git
   cd novaxa-dashboard
   ```

2. Εκτελέστε το script ανάπτυξης:
   ```
   python deploy.py
   ```

3. Το script θα:
   - Ελέγξει τα προαπαιτούμενα
   - Προετοιμάσει τα αρχεία ανάπτυξης
   - Αντιγράψει τα αρχεία της εφαρμογής
   - Δημιουργήσει τα Docker images
   - Αναπτύξει την εφαρμογή με το Docker Compose
   - Επαληθεύσει την ανάπτυξη

4. Μετά την επιτυχή ανάπτυξη, μπορείτε να αποκτήσετε πρόσβαση:
   - Web Dashboard: http://localhost:8080 (ή το domain που έχετε ρυθμίσει)
   - API: http://localhost:5000/api (ή το domain που έχετε ρυθμίσει)

### Ρύθμιση για Παραγωγή

Για ανάπτυξη σε περιβάλλον παραγωγής:

1. Επεξεργαστείτε το αρχείο `deployment/.env` και αλλάξτε:
   ```
   ENVIRONMENT=production
   WEB_URL=https://your-domain.com
   WEBHOOK_ENABLED=True
   WEBHOOK_URL=https://your-domain.com/webhook
   ```

2. Ρυθμίστε το domain σας να δείχνει στον server όπου τρέχει η εφαρμογή

3. Ρυθμίστε το SSL με Let's Encrypt για ασφαλή σύνδεση

## Telegram Bot

Το Telegram bot NOVAXA παρέχει ένα εύχρηστο interface για την παρακολούθηση των μετοχών και των projects σας μέσω του Telegram.

### Διαθέσιμες Εντολές

#### Γενικές Εντολές
- `/start` - Ξεκίνημα του bot
- `/help` - Εμφάνιση μηνύματος βοήθειας
- `/getid` - Εμφάνιση του ID σας
- `/status` - Γενική κατάσταση συστήματος

#### Μετοχές
- `/stocks` - Εμφάνιση όλων των μετοχών
- `/stock [σύμβολο]` - Εμφάνιση συγκεκριμένης μετοχής (π.χ. `/stock OPAP.AT`)
- `/alert [σύμβολο] [τιμή]` - Ορισμός ειδοποίησης για μετοχή (π.χ. `/alert OPAP.AT 18.50`)

#### Projects
- `/projects` - Εμφάνιση όλων των projects
- `/bidprice` - Κατάσταση του BidPrice
- `/amesis` - Κατάσταση του Amesis
- `/6225` - Κατάσταση του Project6225
- `/logs [project]` - Εμφάνιση logs για συγκεκριμένο project (π.χ. `/logs bidprice`)
- `/progress` - Καθημερινή αναφορά προόδου

#### Ειδοποιήσεις
- `/broadcast [μήνυμα]` - Αποστολή μαζικού μηνύματος
- `/notify [μήνυμα]` - Ορισμός ειδοποίησης
- `/trending` - Εμφάνιση τάσεων για Project6225
- `/mystats` - Εμφάνιση στατιστικών για όλα τα projects

### Παραδείγματα Χρήσης

1. Για να δείτε τις τρέχουσες τιμές των μετοχών:
   ```
   /stocks
   ```

2. Για να ορίσετε ειδοποίηση όταν η μετοχή ΟΠΑΠ φτάσει τα 18.50€:
   ```
   /alert OPAP.AT 18.50
   ```

3. Για να δείτε την κατάσταση του project BidPrice:
   ```
   /bidprice
   ```

4. Για να λάβετε την καθημερινή αναφορά προόδου:
   ```
   /progress
   ```

## Web Dashboard

Το Web Dashboard παρέχει μια οπτική διεπαφή για την παρακολούθηση των μετοχών και των projects σας.

### Κύριες Λειτουργίες

1. **Αρχική Σελίδα**
   - Συνοπτική εικόνα των μετοχών και των projects
   - Πρόσφατες ειδοποιήσεις
   - Γρήγορη πρόσβαση σε βασικές λειτουργίες

2. **Σελίδα Μετοχών**
   - Λεπτομερής προβολή των μετοχών
   - Γραφήματα τιμών
   - Ρύθμιση ειδοποιήσεων

3. **Σελίδα Projects**
   - Κατάσταση και πρόοδος των projects
   - Μετρήσεις και στατιστικά
   - Πρόσβαση στα logs

4. **Σελίδα Ειδοποιήσεων**
   - Ιστορικό ειδοποιήσεων
   - Ρύθμιση νέων ειδοποιήσεων
   - Διαχείριση υπαρχόντων ειδοποιήσεων

5. **Σελίδα Ρυθμίσεων**
   - Προσαρμογή του dashboard
   - Ρύθμιση προτιμήσεων ειδοποιήσεων
   - Διαχείριση λογαριασμού

### Πλοήγηση στο Dashboard

- Το πλευρικό μενού παρέχει πρόσβαση σε όλες τις κύριες σελίδες
- Η επάνω γραμμή περιέχει το πεδίο αναζήτησης και τις ειδοποιήσεις
- Το ticker μετοχών στο πάνω μέρος δείχνει τις τρέχουσες τιμές των μετοχών
- Οι κάρτες projects δείχνουν την κατάσταση και την πρόοδο κάθε project

## Παρακολούθηση Μετοχών

Το NOVAXA σας επιτρέπει να παρακολουθείτε τις μετοχές του Χρηματιστηρίου Αθηνών και να λαμβάνετε ειδοποιήσεις για σημαντικές αλλαγές.

### Προσθήκη Μετοχών για Παρακολούθηση

Οι προεπιλεγμένες μετοχές είναι:
- ΟΠΑΠ (OPAP.AT)
- METLEN (MYTIL.AT)

Για να προσθέσετε περισσότερες μετοχές:

1. Στο Telegram bot:
   ```
   /alert [σύμβολο] [τιμή]
   ```

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Μετοχών
   - Κάντε κλικ στο "Προσθήκη Μετοχής"
   - Εισάγετε το σύμβολο και την τιμή-στόχο

### Ρύθμιση Ειδοποιήσεων

Μπορείτε να ορίσετε ειδοποιήσεις για συγκεκριμένες τιμές μετοχών:

1. Στο Telegram bot:
   ```
   /alert OPAP.AT 18.50
   ```

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Μετοχών
   - Κάντε κλικ στο εικονίδιο ειδοποίησης δίπλα στη μετοχή
   - Ορίστε την τιμή-στόχο

### Λήψη Ειδοποιήσεων

Όταν μια μετοχή φτάσει την τιμή-στόχο:

1. Θα λάβετε μήνυμα στο Telegram
2. Θα εμφανιστεί ειδοποίηση στο Web Dashboard
3. Η ειδοποίηση θα καταγραφεί στο ιστορικό ειδοποιήσεων

## Διαχείριση Projects

Το NOVAXA σας επιτρέπει να παρακολουθείτε και να διαχειρίζεστε τα projects σας.

### Προβολή Κατάστασης Projects

1. Στο Telegram bot:
   ```
   /projects
   ```
   ή για συγκεκριμένο project:
   ```
   /bidprice
   /amesis
   /6225
   ```

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Projects
   - Δείτε την κατάσταση όλων των projects
   - Κάντε κλικ σε ένα project για λεπτομέρειες

### Προβολή Logs

1. Στο Telegram bot:
   ```
   /logs bidprice
   ```

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Projects
   - Επιλέξτε ένα project
   - Κάντε κλικ στο "Logs"

### Καθημερινή Αναφορά Προόδου

1. Στο Telegram bot:
   ```
   /progress
   ```

2. Στο Web Dashboard:
   - Η αναφορά προόδου εμφανίζεται στην Αρχική Σελίδα
   - Μπορείτε επίσης να τη δείτε στη σελίδα Projects

## Ειδοποιήσεις και Alerts

Το NOVAXA παρέχει διάφορους τύπους ειδοποιήσεων:

### Τύποι Ειδοποιήσεων

1. **Ειδοποιήσεις Μετοχών**
   - Όταν μια μετοχή φτάσει την τιμή-στόχο
   - Σημαντικές αλλαγές στις τιμές

2. **Ειδοποιήσεις Projects**
   - Αλλαγές στην κατάσταση των projects
   - Ολοκλήρωση εργασιών
   - Νέα logs

3. **Συστημικές Ειδοποιήσεις**
   - Ενημερώσεις συστήματος
   - Προγραμματισμένη συντήρηση
   - Σφάλματα και προβλήματα

### Διαχείριση Ειδοποιήσεων

1. Στο Telegram bot:
   - Χρησιμοποιήστε την εντολή `/notify` για να ορίσετε νέες ειδοποιήσεις
   - Οι ειδοποιήσεις θα σταλούν αυτόματα στο Telegram

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Ειδοποιήσεων
   - Διαχειριστείτε τις υπάρχουσες ειδοποιήσεις
   - Ορίστε νέες ειδοποιήσεις

### Broadcast Μηνύματα

Για να στείλετε μαζικά μηνύματα:

1. Στο Telegram bot:
   ```
   /broadcast Σημαντική ενημέρωση για όλους!
   ```

2. Στο Web Dashboard:
   - Πηγαίνετε στη σελίδα Ειδοποιήσεων
   - Επιλέξτε "Νέο Broadcast"
   - Εισάγετε το μήνυμα και επιλέξτε τους παραλήπτες

## Συντήρηση και Αναβαθμίσεις

### Τακτική Συντήρηση

1. **Αντίγραφα Ασφαλείας**
   - Τα δεδομένα αποθηκεύονται στον όγκο Docker `api_data`
   - Δημιουργήστε τακτικά αντίγραφα ασφαλείας αυτού του όγκου

2. **Έλεγχος Logs**
   - Τα logs του API αποθηκεύονται στο `novaxa_api.log`
   - Τα logs του Web αποθηκεύονται στο `novaxa_integration.log`
   - Τα logs του Bot αποθηκεύονται στο `novaxa_bot.log`

3. **Επανεκκίνηση Υπηρεσιών**
   - Για επανεκκίνηση των υπηρεσιών:
     ```
     cd deployment
     docker-compose restart
     ```

### Αναβαθμίσεις

Για να αναβαθμίσετε το σύστημα:

1. Κάντε pull τις τελευταίες αλλαγές:
   ```
   git pull
   ```

2. Εκτελέστε ξανά το script ανάπτυξης:
   ```
   python deploy.py
   ```

3. Το script θα:
   - Ενημερώσει τα αρχεία
   - Δημιουργήσει νέα Docker images
   - Επανεκκινήσει τις υπηρεσίες με τις νέες εκδόσεις

### Αντιμετώπιση Προβλημάτων

1. **Το Bot δεν ανταποκρίνεται**
   - Ελέγξτε τα logs: `cat novaxa_bot.log`
   - Επανεκκινήστε το bot: `docker-compose restart web`
   - Βεβαιωθείτε ότι το token του bot είναι σωστό

2. **Το Dashboard δεν φορτώνει**
   - Ελέγξτε τα logs: `cat novaxa_integration.log`
   - Επανεκκινήστε το web: `docker-compose restart web`
   - Βεβαιωθείτε ότι το API λειτουργεί

3. **Δεν λαμβάνονται δεδομένα μετοχών**
   - Ελέγξτε τα logs: `cat novaxa_api.log`
   - Επανεκκινήστε το API: `docker-compose restart api`
   - Βεβαιωθείτε ότι υπάρχει σύνδεση στο διαδίκτυο

## Συμπέρασμα

Το NOVAXA Dashboard και Telegram Bot είναι ένα ισχυρό εργαλείο για την παρακολούθηση των μετοχών και των projects σας. Με την ενσωμάτωση του Telegram bot και του web dashboard, έχετε πρόσβαση στις πληροφορίες που χρειάζεστε από οπουδήποτε και οποτεδήποτε.

Για περισσότερες πληροφορίες ή βοήθεια, επικοινωνήστε με την ομάδα υποστήριξης.
