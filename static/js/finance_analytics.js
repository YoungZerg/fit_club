const ctxCompanyIncome = document.getElementById('companyIncomeChart').getContext('2d');
const ctxIncomeDistribution = document.getElementById('incomeDistributionChart').getContext('2d');
const ctxTopCategories = document.getElementById('topCategoriesChart').getContext('2d');
const ctxTopTariffs = document.getElementById('topTariffsChart').getContext('2d');
const ctxOrderStatus = document.getElementById('orderStatusChart').getContext('2d');
const ctxCategoryGraph = document.getElementById('categoryGraph').getContext('2d');

let lineCompanyIncome = new Chart(ctxCompanyIncome, {
    type: 'line',
    data: {
        labels: ['2024-08-01', '2024-08-02', '2024-08-03'], 
        datasets: [
            {
                label: "Доход от товаров",
                backgroundColor: '#EB5135',
                borderColor: '#EB5135',  
                data: [],
                fill: false, 
            },
            {
                label: "Доход от подписок",
                backgroundColor: '#6EEB40', 
                borderColor: '#6EEB40',  
                data: [],
                fill: false, 
            },
            {
                label: "Общий доход",
                backgroundColor: '#2C5CEB',
                borderColor: '#2C5CEB',  
                data: [],
                fill: false, 
            }
        ]
    }
});


let barIncomeDistribution = new Chart(ctxIncomeDistribution, {
    type: "bar",
    data: {
        datasets: [{
            label: "Суммарный доход за период по категориям",
            data: [30, 20, 10],
            backgroundColor: ["#2C5CEB", "#EB5135", "#6EEB40"]
        }]
    }
});


let lineCategoryGraph = new Chart(ctxCategoryGraph, {
    type: "line",
    data: {
        labels: [],  
        datasets: []
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Category Sales Over Time'
        }
    }
});



let barOrderStatus = new Chart(ctxOrderStatus, {
    type: "bar",
    data: {
        labels: [],
        datasets: [{
            label: 'Кол-во заказов по статусам',  
            data: [],  
            backgroundColor: []  
        }],
    },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Order Status Over Time'
        }
    }
});

let barTopCategories = new Chart(ctxTopCategories, {
    type: "bar",
    data: {
        labels: [],
        datasets: [{
            label: 'Топ-3 категорий',
            data: [],
            backgroundColor: []
        }],
    }
}) 






function fetchRevenueData(start_date, end_date){
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

    fetch('/admin/revenue_data', requestOptions)
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const labels = data.products_revenue.map(revenue=>revenue.day);
            const products_revenue = data.products_revenue.map(revenue=>revenue.product_revenue);

            const plans_revenue = data.plans_revenue.map(revenue=>revenue.plan_revenue);

            const total_revenue = data.total_revenue.map(revenue=>revenue.total_revenue);

            const new_data = [products_revenue, plans_revenue, total_revenue];

            let total_revenue_for_period = total_revenue.reduce((partialSum, a) => partialSum + a, 0);

            let total_revenue_products = products_revenue.reduce((partialSum, a) => partialSum + a, 0);

            let total_revenue_plans = plans_revenue.reduce((partialSum, a) => partialSum + a, 0);

            

            const total_revenue_by_categories = [total_revenue_for_period, total_revenue_products, total_revenue_plans];

            updateChart(lineCompanyIncome, labels, new_data)
            updateChart(barIncomeDistribution, ["Суммарный доход за период", "Доход от товаров", "Доход от подписок"], [total_revenue_by_categories])

        })
        .catch(error => {
            console.log("An error occured:", error)
        })
}




function fetchCategoriesData(start_date, end_date){
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

    fetch('/admin/categories_data', requestOptions)
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const labels = data.dates;

            const datasets = data.categories_data.map(category => {
                return {
                    label: category.name,
                    data: category.quantities,
                    fill: false,
                    borderColor: generateRandomColor(),
                };
            });
            

            lineCategoryGraph.data.labels = labels;
            lineCategoryGraph.data.datasets = datasets;
            lineCategoryGraph.update();


            const top_3_labels = data.top_3_categories_data.map(category=> category.name);
            const top_3_data = data.top_3_categories_data.map(category=>category.total_products);
            const colors = top_3_labels.map(() => generateRandomColor());

            

            barTopCategories.data.labels = top_3_labels;
            barTopCategories.data.datasets[0].data = top_3_data;
            barTopCategories.data.datasets[0].backgroundColor = colors;
            barTopCategories.update();


        })
        .catch(error => {
            console.log("An error occured:", error)
        })
}


function fetchOrdersStatusData(start_date, end_date){
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

    fetch('/admin/orders_status', requestOptions)
        .then(response => {
            if(!response.ok){
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const labels = data.map(order=>order.order_status);
            const new_data = data.map(order=>order.orders_quantity);


            const colors = labels.map(() => generateRandomColor());

            barOrderStatus.data.labels = labels;
            barOrderStatus.data.datasets[0].data = new_data;
            barOrderStatus.data.datasets[0].backgroundColor = colors;
            barOrderStatus.update()

        })
        .catch(error => {
            console.log("An error occured:", error)
        })
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

    if(new_data.length == 1){
        chart.data.datasets[0].data = new_data[0];
    }
    else{
        chart.data.datasets.forEach((dataset, index) => {
            if(new_data[index]){
                dataset.data = new_data[index];
            }
        });
    }
    

    chart.update();
}


function generateRandomColor(){
    return '#'+Math.floor(Math.random()*16777215).toString(16)
}