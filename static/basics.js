const form = document.getElementById('upload-form');
const asciiArt = document.getElementById('ascii-art');
const saveBtn = document.getElementById('save-btn');
const moodInput = document.getElementById('mood-input');
const moodDisplay = document.getElementById('mood-display');

form.addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(form);
    const moodValue = moodInput.value.trim();
    formData.append("mood", moodValue);

    fetch('/convert', {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        asciiArt.textContent = data.ascii_art || data.doodle || "No ASCII returned";

        const aff = document.getElementById('affirmation');
        if (aff) aff.textContent = moodValue ? data.affirmation || "" : "";

        const moodTitle = document.getElementById('mood-response');
        if (moodTitle) moodTitle.textContent = data.mood ? "Mood: " + data.mood : "";

        const doodleDiv = document.getElementById("doodle");
        if (doodleDiv) doodleDiv.textContent = data.doodle || "";
    })
    .catch(err => {
        console.error("Error:", err);
        asciiArt.textContent = "Something went wrong!";
    });
});

saveBtn.addEventListener('click', () => {
    const moodValue = moodInput.value.trim();

    if (!moodValue) {
        moodDisplay.textContent = "";
        localStorage.removeItem('mood');
        showMoodMeme("");
        return;
    }

    moodDisplay.textContent = moodValue;
    localStorage.setItem('mood', moodValue);
    showMoodMeme(moodValue);
});

function showMoodMeme(mood) {
    const memeCard = document.getElementById('meme-card');
    const memeImage = document.getElementById('meme-image');
    if (!memeCard || !memeImage) return;

    const moodMemes = {
        happy: '/static/images/happy.jpeg',
        lonely: '/static/images/lonely.jpeg',
        sad: '/static/images/sad.jpeg',
        angry: '/static/images/angry.jpeg',
        tired: '/static/images/tired.jpeg'
    };

    const lowerMood = mood.toLowerCase();
    if (moodMemes[lowerMood]) {
        memeImage.src = moodMemes[lowerMood];
        memeCard.classList.remove('hidden');
        memeCard.classList.add('show');
    } else {
        memeCard.classList.add('hidden');
        memeCard.classList.remove('show');
    }
}
const helperIcon = document.getElementById('helper-icon');
const helperContent = document.getElementById('helper-content');

helperIcon.addEventListener('click', () => {
    helperContent.classList.toggle('show');
});
