let words = [];
let currentIndex = 0;

// Fetch user info
async function fetchUser() {
    try {
        const response = await fetch('/api/user');
        const user = await response.json();
        document.getElementById('user-name').textContent = user.name;
        document.getElementById('user-avatar').src = user.picture;
        document.getElementById('user-avatar').alt = user.name;
    } catch (error) {
        console.error('Error fetching user:', error);
    }
}

// Fetch famous quote
async function fetchQuote() {
    try {
        const response = await fetch('/api/quote');
        const quote = await response.json();
        document.getElementById('quote-text').textContent = `"${quote.text}"`;
        document.getElementById('quote-author').textContent = `— ${quote.author}`;
    } catch (error) {
        console.error('Error fetching quote:', error);
        document.getElementById('quote-text').textContent = 'Error loading quote';
        document.getElementById('quote-author').textContent = '';
    }
}

// Fetch words from API
async function fetchWords() {
    try {
        const response = await fetch('/api/words');
        const data = await response.json();
        words = data;
        document.getElementById('total-words').textContent = words.length;
        if (words.length > 0) {
            displayWord(0);
        }
    } catch (error) {
        console.error('Error fetching words:', error);
        document.getElementById('word').textContent = 'Error loading words';
    }
}

// Fetch note for current word
async function fetchNote(wordId) {
    try {
        const response = await fetch(`/api/notes/${wordId}`);
        const data = await response.json();
        document.getElementById('notes').value = data.notes || '';
    } catch (error) {
        console.error('Error fetching note:', error);
        document.getElementById('notes').value = '';
    }
}

// Save note for current word
async function saveNote() {
    const wordId = words[currentIndex].id;
    const notes = document.getElementById('notes').value;
    const statusEl = document.getElementById('save-status');

    statusEl.textContent = 'Saving...';
    statusEl.className = 'save-status saving';

    try {
        const response = await fetch(`/api/notes/${wordId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ notes: notes })
        });

        if (response.ok) {
            statusEl.textContent = 'Saved!';
            statusEl.className = 'save-status';
            setTimeout(() => {
                statusEl.textContent = '';
            }, 2000);
        } else {
            throw new Error('Failed to save note');
        }
    } catch (error) {
        console.error('Error saving note:', error);
        statusEl.textContent = 'Error saving';
        statusEl.className = 'save-status error';
        setTimeout(() => {
            statusEl.textContent = '';
        }, 3000);
    }
}

// Display current word
function displayWord(index) {
    if (index < 0 || index >= words.length) return;

    currentIndex = index;
    const word = words[index];

    document.getElementById('word').textContent = word.word;
    document.getElementById('translation').textContent = word.polish_translation;
    document.getElementById('example-1').textContent = '1. ' + word.example_sentence_1;
    document.getElementById('example-2').textContent = '2. ' + word.example_sentence_2;
    document.getElementById('example-3').textContent = '3. ' + word.example_sentence_3;
    document.getElementById('current-word').textContent = index + 1;

    // Load note for this word
    fetchNote(word.id);

    // Update button states
    document.getElementById('prev-btn').disabled = (index === 0);
    document.getElementById('next-btn').disabled = (index === words.length - 1);
}

// Navigate to previous word
function previousWord() {
    if (currentIndex > 0) {
        displayWord(currentIndex - 1);
    }
}

// Navigate to next word
function nextWord() {
    if (currentIndex < words.length - 1) {
        displayWord(currentIndex + 1);
    }
}

// Event listeners for buttons
document.getElementById('prev-btn').addEventListener('click', previousWord);
document.getElementById('next-btn').addEventListener('click', nextWord);
document.getElementById('save-note-btn').addEventListener('click', saveNote);

// Keyboard navigation
document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft') {
        previousWord();
    } else if (event.key === 'ArrowRight') {
        nextWord();
    }
});

// Load user info, words, and quote on page load
fetchUser();
fetchWords();
fetchQuote();
