$(document).ready(function() {
    // Flask からテンプレートエンジンで変数を埋め込む
    var currentYear = {{ year | tojson }};
    var currentMonth = {{ month | tojson }} - 1;  // JavaScriptの月は0始まりなので1引きます
    
    // カレンダーの初期化
    var calendar = $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        events: function(start, end, timezone, callback) {
            $.ajax({
                url: '/get_memos',
                dataType: 'json',
                success: function(data) {
                    var events = data.map(function(memo) {
                        return {
                            title: memo.content,
                            start: memo.date,
                            allDay: true
                        };
                    });
                    callback(events);
                }
            });
        },
        dayClick: function(date, jsEvent, view) {
            // 日付クリック時にメモフォームに選択された日付をセット
            $('#memoDate').text(date.format('YYYY-MM-DD'));
            $('#memoDateInput').val(date.format('YYYY-MM-DD'));
            $('#memoForm').show(); // メモ追加フォームを表示
        },
        // 年月が変更された際に新しい月を設定
        defaultView: 'month',
        defaultDate: moment({ year: currentYear, month: currentMonth }).format('YYYY-MM-DD'), // momentの正しい使い方
        locale: 'ja',  // 日本語設定
    });

    // selectボックスで年月を変更した際にカレンダーを更新
    $('#yearSelect, #monthSelect').change(function() {
        var newYear = $('#yearSelect').val();
        var newMonth = $('#monthSelect').val() - 1;  // JavaScriptの月は0始まり
        calendar.fullCalendar('gotoDate', new Date(newYear, newMonth, 1));  // 新しい月を表示
    });
});
