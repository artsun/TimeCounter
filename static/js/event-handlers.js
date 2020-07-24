

async function send_selected_date(data, elem) {
	selected_date = new Date(data['date']);
    window.location.replace(`?day=${selected_date.getDate()}&month=${selected_date.getMonth()+1}&year=${selected_date.getFullYear()}`);
}

window.setTime = function (h, m, s){
    h_d = (h < 10) ? "0" + h : h;
    m_d = (m < 10) ? "0" + m : m;
    s_d = (s < 10) ? "0" + s : s;

    let time = h_d + ":" + m_d + ":" + s_d;
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;
};
