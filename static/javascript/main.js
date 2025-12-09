function playSong(url, track_id) {
    const player = document.getElementById("audio-player");
    const image_element = document.getElementById("play-button-image-" + track_id);


    let all_images = Array.from(document.getElementsByClassName("play-button-image"));
    all_images.forEach((element) => element.src = play_image);

    if(player.src != "" && player.src.includes(url)) {
        if (player.paused) {
            image_element.src = pause_image;
            player.play();
        } else {
            image_element.src = play_image;
            player.pause();
        }
    }
    else {
        player.src = url;
        player.play();
        image_element.src = pause_image;
    }
}

function openLogin(){
    let login_form = document.getElementsByClassName("menu-box-user")[0];
    if(login_form.style.display.toString() == "none") login_form.style.display = "flex";
    else login_form.style.display = "none";
}

async function toggleLikedTrack(track_id) {
    const like_button_element = document.getElementById("button_liked_" + track_id);
    const current_url = like_button_element.src;

    if(current_url === liked_image_url) {
        like_button_element.src = unliked_image_url;
        await fetch(`/unlike/${track_id}`, { method: "POST" });
    }
    else{
        like_button_element.src = liked_image_url;
        await fetch(`/like/${track_id}`, { method: "POST" });
    }
}

async function open_url(url) { window.location.href = url; }

function initializePlayButton(element_id, track_path) {
    const player = document.getElementById("audio-player");
    if(player.src.includes(track_path.trim()) && !player.paused) {
        document.getElementById(element_id).src = pause_image;
    }
}

function toggleOverlayMenu(element_id) {
    document.getElementById(element_id).classList.toggle('overlay-menu-visible');
    document.getElementById(element_id).classList.toggle('overlay-menu-hidden');
}

async function changeProfileToArtist(){
    await fetch(`/changetoartist`, { method: "POST" });
}