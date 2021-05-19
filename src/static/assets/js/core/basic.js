const main_card = document.getElementById("vis")
const paper_frame = document.getElementById("paper_frame")
const paper_title = document.getElementById("paper_title")
const search_bar = document.getElementById("search_bar")
const search_button = document.getElementById("search_button")
const current_zoom = {x: null, y: null, timeline: null}
var provenance = {events: []}
var global_paper_data = {paper_data: null};
var global_keywords = null;
var dt_from = "1970-05-04";
var dt_to= "2015-12-01";

document.onclick = ((event) => add_event_to_prov("mouse click"))
search_bar.onclick = ((event) => add_event_to_prov("search bar clicked"))
search_button.onclick = ((event) =>{
    // TODO: Presreve zoom level after query search
    add_event_to_prov(`search button clicked ${document.getElementById("search_bar").value}`);
    global_keywords = document.getElementById("search_bar").value
    if(search_bar.value){
        server_call(`/get-paper-data/${dt_from}/${dt_to}/${search_bar.value}`).then((resp) => {
            timeline("vis",resp, 1500, 25, [150, 440]); 
        })
    } else {
            server_call(`/get-paper-data/${dt_from}/${dt_to}/`).then((resp) => {
                timeline("vis",resp, 1500, 25, [150, 440]); 
            });
    }
    render_iframe(global_paper_data, search_bar.value);
})



function add_event_to_prov(name){
    provenance.events.push({name: name, timestamp: (new Date())});
}

function make_newspaper_link(paper_id, keyword = null){
    var libumd = `https://iiif.lib.umd.edu/viewer/1.2.0/mirador.html?manifest=fcrepo:pcdm::${paper_id}&iiifURLPrefix=https://iiif.lib.umd.edu/manifests/${keyword?"&q=".concat(keyword):""}`;
    console.log(libumd);
    console.log(keyword);
    return libumd;
}


function server_call(end_point){
    console.log(end_point);
    let url = new URL("http://localhost:8000/" + end_point);
    url.search = new URLSearchParams().toString();
    return fetch(url,{"credentials": "same-origin"})
        .then(response => response.json())
        .then(function(response){
            add_event_to_prov(`server call to ${end_point}`)
            return response;
        });
}


server_call(`/get-paper-data/${dt_from}/${dt_to}`).then((resp) => {
    timeline("vis",resp, 1500, 25, [150, 440]); 
});

function render_iframe(paper_data, keyword){
    if(!keyword){keyword = search_bar.value;}
    let title = document.getElementById('paper_title');
    let body = document.getElementById('paper_frame');
    title.textContent = paper_data.title;
    body.innerHTML = 
        `<center><iframe title="" width="1000px" height="600px"src='${make_newspaper_link(paper_data.paper_id, keyword)}' frameborder="0"></iframe></center>`
    body.onmouseover = function(){
        add_event_to_prov("over the iframe")
    }
    body.onmouseleave = function(){
        add_event_to_prov("off the iframe")
    }
    body.onmouseup = function(){
        add_event_to_prov("clicked the iframe")
    }

}

function end_exploration(){
    add_event_to_prov("End exploration")
    return provenance;
}

// assuming that you have an id and not a class
function timeline(object_id, response, width, line_height, margin = [0, 0]){
    // initializing the timeline region with an svg
    // var svg = d3.select(object_id).append("svg").attr("width", width).attr("height", height)
    var dt_from = "1970-05-04";
    var dt_to= "2015-12-01";

    for(g_id in response){
        let group = response[g_id]
        for(l_id in group.data){
            let label = group.data[l_id];
            for(d_id in label.data){
                let date = label.data[d_id].timeRange;
                date = date.map((x) => new Date(x));
                response[g_id].data[l_id].data[d_id].timeRange = date;
            }
        }
    }
    //margin left = 150
    //margin right = 440

    const vis = document.getElementById(object_id)
    vis.textContent = ''
    vis.onmouseover = ((x) => add_event_to_prov("over the chart"));
    TimelinesChart()
        .width(width)
        .zQualitative(true)
        .maxLineHeight(line_height)
        .leftMargin(margin[0])
        .rightMargin(margin[1])
        .data(response)
        .onSegmentClick(function(segment){
            let paper_data = segment.srcElement.__data__.data;
            global_paper_data = paper_data;
            render_iframe(paper_data)
            add_event_to_prov(`segment clicked: ${paper_data.title}`)
        })
        .segmentTooltipContent(function(segment){
            let paper_data = segment.data;
            return paper_data.title;
        })
        .zColorScale(d3.scaleOrdinal()
            .domain(["No Keywords"])
            .range(["steelblue",  "orange"])
        )
    (vis);
}
