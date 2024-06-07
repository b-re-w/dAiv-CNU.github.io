from browser import document, window, aio, module_init
print, pyprint = module_init(__name__, "contest.coding.shared")
from common.dashboard import build_timeline_chart, build_participation_status_chart, build_leaderboard_chart
from datetime import datetime
from random import choice
import traceback
import json


def parse_timeline_data():
    date_format = "%Y년 %m월 %d일"
    date = lambda d: datetime.strptime(d, date_format).date()

    application_period = document['application_period'].textContent.split(": ")[1]
    contest_period = document['contest_period'].textContent.split(": ")[1]
    result_announcement = document['result_announcement'].textContent.split(": ")[1]

    appl = application_period.split(" (")[0]
    start, end, *_ = contest_period.split(" (")
    end = end.split("~ ")[1]
    result = result_announcement.split(" (")[0]
    timeline = date(appl), date(start), date(end), date(result)
    return timeline


########################################################################################################################
# AOS Animation
########################################################################################################################
window.AOS.init()


########################################################################################################################
# Timeline Animation
########################################################################################################################
try:
    window.ApexCharts.new(document.querySelector("#timeline_radial_bar_chart"),
                          build_timeline_chart(parse_timeline_data())
                          ).render()
except Exception as _:
    traceback.print_exc()


########################################################################################################################
# Participation Status Animation
########################################################################################################################
try:
    chart = document.querySelector("#participants_status_chart")
    if chart.attributes.data.value:
        dataset = list(map(int, chart.attributes.data.value.replace(' ', '').split(',')))
    else:
        dataset = []
        raise NotImplementedError("Please implement other dataset query methods.")

    total_team = sum(dataset)
    count_desc = document.getElementById('participants_count_desc')
    count = document.getElementById('participants_count')
    if count_desc:
        count_desc.innerHTML = count_desc.innerHTML.replace("{participants}", f"{total_team}")
    if count:
        count.innerHTML = count.innerHTML.replace("{participants}", f"{total_team}")

    chart_wrapper = document.getElementById('participants_status_chart_wrapper')
    if chart_wrapper:
        chart_wrapper.classList.add(choice(['chart-wrapper-var0', 'chart-wrapper-var1']))

    window.ApexCharts.new(chart, build_participation_status_chart(dataset, parse_timeline_data())).render()
except Exception as _:
    traceback.print_exc()


########################################################################################################################
# QnA
########################################################################################################################
async def set_iframe():
    try:
        pushoong = window.frames['pushoong'].document
    except Exception as _:
        traceback.print_exc()
        print("QNA- iframe not found. terminating set_iframe()...")
        pushoong = None

    psh_req = await window.fetch(document.getElementsByName("pushoong")[0].attributes.data.value)
    psh_html = ((await psh_req.text()).replace("115px", "0px")
                .replace("//t1.daumcdn.net/kas/static/ba.min.js", "")
                .replace("Kakao.init('4cca00b63eedb801abfc9952db0ee7a3');", "")
                .replace("<head>", "<head>"
                                    "<base href=\"https://pushoong.com/\">"
                                    "<link href=\""+window.location.origin+"/dist/res/css/font.css\" rel=\"stylesheet\">"
                                    "<style>.increase_max_width {max-width: 1000px !important;}</style>")
                .replace("<body>", "<body style=\"background-color: #fff;\">")
                .replace("<div class=\"container\">", "<div class=\"container\" style=\"background-color: #fff;\">")
                .replace("<div id=\"fullscreen-overlay\">", "<div id=\"fullscreen-overlay-disabled\" style=\"display:none;\">")
                .replace("<div class=\"attach_border\" style=\"", "<div class=\"attach_border\" style=\"display:none;")
                .replace("input_border col", "col mt-1 ml-1\" onclick=\"window.open('https://pushoong.com/ask/7395560693', '_blank');")
                .replace("id=\"ask_send\"", "id=\"ask_send_disabled\"")
                .replace("<div class = \"container\">", "<div class = \"increase_max_width container\">")
                .replace("ask_wrapper not_host", "increase_max_width ask_wrapper not_host")
                .replace("ask_title_zone", "increase_max_width ask_title_zone")
                .replace("ask_input_zone", "increase_max_width ask_input_zone"))

    if pushoong:
        pushoong.open()
        pushoong.write(psh_html)
        pushoong.close()

aio.run(set_iframe())


########################################################################################################################
# Leaderboard settings
########################################################################################################################
def open_leaderboard(e):
    try:
        async def remove_show_button(btn):
            value = btn.offsetHeight
            while True:
                if value < 0:
                    break
                elif value < 15:
                    btn.innerHTML = ""
                    btn.style.padding = "1.5px"
                value -= 1
                btn.style.height = f"{value}px"
                await aio.sleep(0.005)

        async def remove_hider(obj):
            value = 1
            while True:
                if value < 0:
                    break
                value -= 0.01
                obj.style.opacity = f"{value}"
                await aio.sleep(0.01)
            obj.remove()

        aio.run(remove_show_button(e.currentTarget))
        hider = document.getElementById('leaderboard_hider')
        if hider:
            aio.run(remove_hider(hider))
    except Exception as _:
        traceback.print_exc()


try:
    leaderboard = document.querySelector("#leaderboard_chart")
    if leaderboard.innerHTML:
        raw_data = leaderboard.innerHTML
        leaderboard.innerHTML = ""
        dataset = json.loads(raw_data, parse_float=lambda x: float(x))
    else:
        dataset = {}
        raise NotImplementedError("Please implement other dataset query methods.")

    # arrange dataset
    # # select sorting criteria
    criteria = ""
    keys = list(dataset['values'].keys())
    keys.reverse()
    for key in keys:  # dict(reversed(a['values'].items())) not working properly in brython
        criteria = key
        if sum(dataset['values'][key]) > 0:
            break
    # # sort
    if criteria:
        zipped = zip(dataset['values'][criteria], zip(dataset['teams'], *dataset['values'].values()))
        sorted_zip = [value for key, value in sorted(zipped, key=lambda x: x[0], reverse=True)]
        unzipped = list(zip(*sorted_zip))
        dataset['teams'] = unzipped.pop(0)
        dataset['values'] = {key: dt for dt, key in zip(unzipped, dataset['values'].keys())}

    chart = window.ApexCharts.new(leaderboard, build_leaderboard_chart(**dataset))
    chart.render()
    [chart.toggleSeries(key) for key in keys if sum(dataset['values'][key]) <= 0]

    opener = document.getElementById('btn_leaderboard')
    if opener:
        opener.bind('click', open_leaderboard)
except Exception as _:
    traceback.print_exc()


########################################################################################################################
# Winner Poduim settings
########################################################################################################################
def open_winnerpodium(e):
    try:
        result_panel = document['winnerpodium_result_panel']
        if result_panel:
            async def show_result(pan):
                value = 0
                while True:
                    if value > 1:
                        break
                    value += 0.01
                    pan.style.opacity = f"{value}"
                    await aio.sleep(0.01)

            aio.run(show_result(result_panel))

        async def remove_show_button(btn):
            value = 1
            while True:
                if value < 0:
                    break
                value -= 0.01
                btn.style.opacity = f"{value}"
                await aio.sleep(0.01)

        aio.run(remove_show_button(e.currentTarget))
    except Exception as _:
        traceback.print_exc()


try:
    opener = document['btn_open_winnerpodium']
    if opener:
        opener.bind('click', open_winnerpodium)
    panel = document['winnerpodium_result_panel']
    if panel:
        panel.style.opacity = "0"
except Exception as _:
    traceback.print_exc()
