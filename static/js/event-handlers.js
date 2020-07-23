

async function send_selected_date(data, elem) {
	selected_date = new Date(data['date']);
    window.location.replace(`?day=${selected_date.getDate()}&month=${selected_date.getMonth()+1}&year=${selected_date.getFullYear()}`);
}
