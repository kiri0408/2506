(() => {
  const calendarEl = document.getElementById('calendar');
  const monthLabel = document.getElementById('month-label');
  const prevMonthBtn = document.getElementById('prev-month');
  const nextMonthBtn = document.getElementById('next-month');
  const modal = document.getElementById('modal');
  const modalCloseBtn = document.getElementById('modal-close');
  const saveScheduleBtn = document.getElementById('save-schedule');
  const scheduleTextarea = document.getElementById('schedule-textarea');

  let currentYear, currentMonth;
  let schedules = {};
  let selectedDate = null;

  const dayNames = ['日', '月', '火', '水', '木', '金', '土'];

  function formatDate(year, month, day) {
    return `${year.toString().padStart(4, '0')}-${(month+1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
  }

  function updateMonthLabel() {
    monthLabel.textContent = `${currentYear}年 ${currentMonth + 1}月`;
  }

  function clearCalendar() {
    calendarEl.innerHTML = '';
  }

  function createDayNameHeaders() {
    dayNames.forEach(dayName => {
      const div = document.createElement('div');
      div.className = 'day-name';
      div.textContent = dayName;
      calendarEl.appendChild(div);
    });
  }

  function openModal(dateStr) {
    selectedDate = dateStr;
    scheduleTextarea.value = schedules[dateStr] || '';
    modal.style.display = 'flex';
    scheduleTextarea.focus();
  }

  function closeModal() {
    modal.style.display = 'none';
    selectedDate = null;
    scheduleTextarea.value = '';
  }

  function fetchSchedules(year, month) {
    return fetch(`/api/schedules?year=${year}&month=${month + 1}`)
      .then(res => {
        if (!res.ok) throw new Error('予定の取得に失敗しました');
        return res.json();
      });
  }

  function saveSchedule(dateStr, text) {
    return fetch('/api/schedules', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({date: dateStr, text: text})
    }).then(res => {
      if (!res.ok) throw new Error('予定の保存に失敗しました');
      return res.json();
    });
  }

  function renderCalendar() {
    clearCalendar();
    createDayNameHeaders();

    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const firstWeekday = firstDay.getDay();
    const daysInMonth = lastDay.getDate();

    // Calculate total cells: days + leading blanks to align first day
    const totalCells = firstWeekday + daysInMonth;
    // We will fill a grid of 7 columns and enough rows to fit all days
    const rows = Math.ceil(totalCells / 7);

    // Fill leading empty cells for previous month
    for (let i = 0; i < firstWeekday; i++) {
      const cell = document.createElement('div');
      cell.className = 'date-cell inactive';
      calendarEl.appendChild(cell);
    }

    // Fill days of current month
    for (let day = 1; day <= daysInMonth; day++) {
      const cell = document.createElement('div');
      cell.className = 'date-cell';
      const dateStr = formatDate(currentYear, currentMonth, day);

      const dateNumberEl = document.createElement('div');
      dateNumberEl.className = 'date-number';
      dateNumberEl.textContent = day;
      cell.appendChild(dateNumberEl);

      const scheduleTextEl = document.createElement('div');
      scheduleTextEl.className = 'schedule-text';
      scheduleTextEl.textContent = schedules[dateStr] || '';
      cell.appendChild(scheduleTextEl);

      cell.addEventListener('click', () => {
        openModal(dateStr);
      });

      calendarEl.appendChild(cell);
    }

    // Fill trailing empty cells to complete the grid if needed
    const trailingCells = rows * 7 - totalCells;
    for (let i = 0; i < trailingCells; i++) {
      const cell = document.createElement('div');
      cell.className = 'date-cell inactive';
      calendarEl.appendChild(cell);
    }
  }

  function loadAndRender() {
    fetchSchedules(currentYear, currentMonth)
      .then(data => {
        schedules = data;
        renderCalendar();
        updateMonthLabel();
      })
      .catch(err => {
        alert(err.message);
      });
  }

  prevMonthBtn.addEventListener('click', () => {
    if (currentMonth === 0) {
      currentYear--;
      currentMonth = 11;
    } else {
      currentMonth--;
    }
    loadAndRender();
  });

  nextMonthBtn.addEventListener('click', () => {
    if (currentMonth === 11) {
      currentYear++;
      currentMonth = 0;
    } else {
      currentMonth++;
    }
    loadAndRender();
  });

  saveScheduleBtn.addEventListener('click', () => {
    if (!selectedDate) return;
    const text = scheduleTextarea.value.trim();
    saveSchedule(selectedDate, text)
      .then(() => {
        schedules[selectedDate] = text;
        closeModal();
        renderCalendar();
      })
      .catch(err => {
        alert(err.message);
      });
  });

  modalCloseBtn.addEventListener('click', () => {
    closeModal();
  });

  // Close modal on outside click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Initialize current year and month to today
  const today = new Date();
  currentYear = today.getFullYear();
  currentMonth = today.getMonth();

  loadAndRender();
})();
