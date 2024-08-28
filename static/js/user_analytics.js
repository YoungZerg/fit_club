// Example charts using Chart.js



// User Distribution Pie Chart
const userDistributionChartCtx = document.getElementById('userDistributionChart').getContext('2d');
new Chart(userDistributionChartCtx, {
    type: 'pie',
    data: {
        labels: ['Зареганы', 'Незареганы'],
        datasets: [{
            data: [38, 137],
            backgroundColor: ['#FF6384', '#FFCD56']
        }]
    }
});

// Visitor Graph Line Chart
const visitorGraphCtx = document.getElementById('visitorGraph').getContext('2d');
new Chart(visitorGraphCtx, {
    type: 'line',
    data: {
        labels: ['2024-08-01', '2024-08-02', '2024-08-03'], // Example dates
        datasets: [{
            label: 'Число посетителей',
            data: [50, 60, 40], // Example data
            borderColor: '#FF6384',
            fill: false,
            tension: 0.1,
            pointRadius: 4,
            pointBackgroundColor: '#FF6384'
        }]
    }
});

// Class Registration Bar Chart
const classRegistrationChartCtx = document.getElementById('classRegistrationsChart').getContext('2d');
let barClassRegistration = new Chart(classRegistrationChartCtx, {
    type: 'bar',
    data: {
        datasets: [{
            label: 'Кол-во участников',
        }]
    }
});

// Top 3 Classes Horizontal Bar Chart
const topClassesChartCtx = document.getElementById('topClassesChart').getContext('2d');
let batTopClasses = new Chart(topClassesChartCtx, {
    type: 'bar',
    data: {
        datasets: [{
            label: 'Кол-во участников',
        }]
    },
    options: {
        indexAxis: 'y',
    }
});

// Top 3 Trainers Horizontal Bar Chart
const topTrainersChartCtx = document.getElementById('topTrainersChart').getContext('2d');
let barTopTrainers = new Chart(topTrainersChartCtx, {
    type: 'bar',
    data: {
        datasets: [{
            label: 'Кол-во записей у тренера',
        }]
    },
    options: {
        indexAxis: 'y',
    }
});


var currentDateOption = document.getElementById('date-select')
currentDateOption.addEventListener('change', dateTracker)

function dateTracker(){
    console.log(currentDateOption.value)
}



function fetchCoursePopularity(start_date, end_date){
    const postData = {
        "start_date": start_date,
        "end_date": end_date
    };
      
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    };

    fetch('/admin/class_statistics', requestOptions)
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const labels = data.map(element => element.course_name);
            const new_data = data.map(element => element.course_participants);

            const top_3_labels = labels.slice(0, 3);
            const top_3_data = new_data.slice(0, 3);

            updateChart(barClassRegistration, labels, new_data);
            updateChart(batTopClasses, top_3_labels, top_3_data);

        })
        .catch(error => {
            console.log("An error occured:", error)
        })
    
}

function fetchTrainerPopularity(start_date, end_date){
    const postData = {
        "start_date": start_date,
        "end_date": end_date
    };
      
    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(postData)
    };

    fetch('/admin/trainers_statistics', requestOptions)
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const labels = data.map(element => element.trainer_name);
            const new_data = data.map(element => element.trainer_clients);

            updateChart(barTopTrainers, labels, new_data);
        })
        .catch(error => {
            console.log("An error occured:", error)
        })
}



function generateRandomColor(){
    return '#'+Math.floor(Math.random()*16777215).toString(16)
}

function removeData(chart) {
    chart.data.labels = [];
    chart.data.datasets.forEach((dataset) => {
        dataset.data = [];
    });
    chart.update();
}


function updateChart(chart, label, new_data){
    removeData(chart);
    chart.data.labels = label;
    chart.data.datasets[0].data = new_data;
    let colors = []
    for(let i = 0; i < label.length;i++){
        let rn_col = generateRandomColor() 
        console.log(rn_col);
        colors.push(rn_col);
    }
    chart.data.datasets[0].backgroundColor = colors;
    chart.update();
}

