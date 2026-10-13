document.addEventListener('DOMContentLoaded', () => {
  // 1. 根據網址參數載入班級設定 (例如 ?class=dawei_studio_01)
  loadClassConfig();

  // 2. 初始化 NPS 0~10 分按鈕
  initNpsScale();

  // 3. 初始化星級評分 (Star Ratings)
  initStarRatings();

  // 4. 初始化標籤選擇器 (Progress tags)
  initTagSelectors();

  // 5. 初始化好禮兌換動態展開切換
  initRewardToggle();

  // 6. 初始化學習吃力「其他」輸入框動態切換
  initStruggleOtherToggle();

  // 7. 表單提交處理
  initFormSubmit();
});

// 動態載入班級設定
async function loadClassConfig() {
  const urlParams = new URLSearchParams(window.location.search);
  const classId = urlParams.get('class');
  if (classId && document.getElementById('classIdInput')) {
    document.getElementById('classIdInput').value = classId;
  }

  try {
    const reqUrl = classId ? `/api/class-info?class_id=${classId}` : '/api/class-info';
    const res = await fetch(reqUrl);
    if (!res.ok) return;
    const data = await res.json();
    if (document.getElementById('classIdInput')) {
      document.getElementById('classIdInput').value = data.class_id || classId || 'class_1791862849';
    }

    // 判斷是否開啟完課好禮課程 (以資料明確標記為準，未開啟則為純回饋模式)
    window.isGiftEnabled = (data.enable_gift === true);
    const isGift = window.isGiftEnabled;

    const badgeEl = document.getElementById('badgeText');
    const titleEl = document.getElementById('courseTitle');
    const subtitleEl = document.getElementById('courseSubtitle');
    const pill1El = document.getElementById('pill1');
    const pill2El = document.getElementById('pill2');
    const pill3El = document.getElementById('pill3');

    // 課程名稱與網頁標題
    if (data.course_name && titleEl) {
      titleEl.textContent = data.course_name;
      document.title = isGift 
        ? `${data.course_name} 結業回饋 ＆ 線上單元課兌換` 
        : `${data.course_name} 結業學習成果回饋問卷`;
    }

    // Badge 膠囊標籤
    if (badgeEl) {
      if (isGift) {
        badgeEl.textContent = (data.badge_text && !data.badge_text.includes('匿名')) 
          ? data.badge_text 
          : '🎁 結業學習回饋 ✕ 限時專屬好禮';
      } else {
        const raw = (data.badge_text || '').trim();
        if (!raw || /好禮|贈|兌換|免費/.test(raw)) {
          badgeEl.textContent = '📝 結業學習成果回饋';
        } else {
          badgeEl.textContent = raw;
        }
      }
    }

    // 副標題 (嚴格解耦贈課文字)
    if (subtitleEl) {
      if (isGift) {
        subtitleEl.textContent = data.course_subtitle || '結業成果驗收 ＆ 免費加碼單元課兌換';
      } else {
        let clean = (data.course_subtitle || '')
          .replace(/[＆&＋+]\s*免費加碼單元課兌換/g, '')
          .replace(/[＆&＋+]\s*線上單元課免費兌換/g, '')
          .replace(/[＆&＋+]\s*實戰單元課免費兌換/g, '')
          .replace(/[＆&＋+]\s*精選單元課免費兌換/g, '')
          .replace(/[＆&＋+]\s*精選加值單元課免費兌換/g, '')
          .replace(/免費加碼單元課兌換/g, '')
          .replace(/線上單元課免費兌換/g, '')
          .trim();
        if (!clean || /兌換|好禮|單元課|加碼/.test(clean)) {
          clean = '結業學習成果驗收 ＆ 教學成效回饋';
        }
        subtitleEl.textContent = clean;
      }
    }

    if (data.gift_banner_title && document.getElementById('giftBannerTitle')) {
      document.getElementById('giftBannerTitle').textContent = data.gift_banner_title;
    }
    if (data.gift_banner_desc && document.getElementById('giftBannerDesc')) {
      document.getElementById('giftBannerDesc').textContent = data.gift_banner_desc;
    }

    if (data.pill_1 && pill1El) pill1El.textContent = data.pill_1;
    if (data.pill_2 && pill2El) pill2El.textContent = data.pill_2;
    if (pill3El) {
      if (isGift) {
        if (data.pill_3 && /好禮|贈|單元課/.test(data.pill_3)) {
          pill3El.textContent = data.pill_3;
        } else if (data.pill_3 && !/匿名/.test(data.pill_3)) {
          pill3El.textContent = data.pill_3;
        } else {
          pill3El.textContent = '🎁 完填即贈單元課';
        }
      } else {
        if (data.pill_3 && !/好禮|贈|單元課/.test(data.pill_3)) {
          pill3El.textContent = data.pill_3;
        } else {
          pill3El.textContent = '✨ 匿名填答';
        }
      }
    }

    if (data.teacher_name) {
      document.querySelectorAll('.teacher-name-span').forEach(el => {
        el.textContent = `${data.teacher_name}老師`;
      });
    }

    // 依據好禮設定即時套用顯隱邏輯
    applyGiftVisibility();

    // 動態載入單元課清單
    if (data.reward_courses && data.reward_courses.length > 0) {
      const container = document.getElementById('rewardCourseList');
      if (container) {
        container.innerHTML = '';
        data.reward_courses.forEach((c, idx) => {
          const label = document.createElement('label');
          label.className = 'reward-card';
          label.innerHTML = `
            <input type="radio" name="selected_reward_course" value="${c}" required ${idx === 0 ? 'checked' : ''}>
            <div class="reward-card-body">
              <span class="badge-free">免費兌換</span>
              <strong>${c}</strong>
              <small>由後台專員核對資料後，於 1~2 工作天內主動聯繫開通</small>
            </div>
          `;
          container.appendChild(label);
        });
      }
    }

    // 動態載入課綱重點晶片
    if (data.syllabus_topics && data.syllabus_topics.length > 0) {
      const topicChips = document.getElementById('syllabusTopicChips');
      const topicList = document.getElementById('syllabusTopicList');
      if (topicChips && topicList) {
        topicList.innerHTML = '';
        data.syllabus_topics.forEach(t => {
          const chip = document.createElement('span');
          chip.className = 'topic-chip';
          chip.textContent = t;
          topicList.appendChild(chip);
        });
        topicChips.style.display = 'block';
      }
    }

    // 動態載入學習痛點選項 (若課綱有生成專屬選項)
    if (data.struggle_options && data.struggle_options.length > 0) {
      const struggleContainer = document.getElementById('strugglePointContainer');
      if (struggleContainer) {
        struggleContainer.innerHTML = '';
        data.struggle_options.forEach((opt, idx) => {
          const label = document.createElement('label');
          label.className = 'radio-item';
          label.innerHTML = `
            <input type="radio" name="struggle_point" value="${opt}" required ${idx === 0 ? 'checked' : ''}>
            <span>${opt}</span>
          `;
          struggleContainer.appendChild(label);
        });
        // 加入其他選項
        const otherLbl = document.createElement('label');
        otherLbl.className = 'radio-item';
        otherLbl.innerHTML = `
          <input type="radio" name="struggle_point" value="其他">
          <span>其他</span>
        `;
        struggleContainer.appendChild(otherLbl);
        initStruggleOtherToggle();
      }
    }

    // 獨立處理 12. 延伸進階主題意願調查
    const isTopicEnabled = (data.enable_followup_topics !== false);
    window.isFollowupTopicEnabled = isTopicEnabled;
    const topicSection = document.getElementById('followupTopicSection');

    // 獨立處理 13. 開課課表梯次 ＆ 舊生早鳥優惠
    const isScheduleEnabled = (data.enable_followup_schedules !== false);
    window.isFollowupScheduleEnabled = isScheduleEnabled;
    const scheduleSection = document.getElementById('followupScheduleSection');

    const rewardSection = document.getElementById('rewardRedemptionSection');

    // 自適應動態題號編排 (NPS評分之後)
    let currentStep = 5;

    if (topicSection) {
      if (!isTopicEnabled) {
        topicSection.style.display = 'none';
      } else {
        topicSection.style.display = 'block';
        const stepNumEl = document.getElementById('followupTopicStepNum');
        if (stepNumEl) stepNumEl.textContent = String(currentStep).padStart(2, '0');
        currentStep++;

        // 題目文字更新講師姓名
        const topicQuestionLabel = document.getElementById('followupTopicQuestionLabel');
        const teacherName = data.teacher_name || '講師';
        if (topicQuestionLabel) {
          topicQuestionLabel.innerHTML = `未來若由【${teacherName}老師】開設進階主題，您最希望深入挑戰的方向是？ <small class="hint">（可協助教學團隊為大家規劃下梯次進階大綱）</small>`;
        }

        // 動態渲染延伸進階主題選項 (單選)
        const topicsContainer = document.getElementById('followupTopicsContainer');
        if (topicsContainer) {
          topicsContainer.innerHTML = '';
          const topics = (data.followup_topics && data.followup_topics.length > 0)
            ? data.followup_topics
            : [
                "進階 A：商業場景氛圍光影 ✕ 概念美術完稿實戰班",
                "進階 B：日系動畫 Layout 分鏡 ✕ 鏡頭空間透視大師班",
                "進階 C：數位繪畫商業接案與作品集專案指導班"
              ];

          topics.forEach(top => {
            const lbl = document.createElement('label');
            lbl.className = 'radio-card compact';
            lbl.innerHTML = `
              <input type="radio" name="followup_interest_topic" value="${top}">
              <div class="card-body">
                <span class="emoji">🎨</span>
                <strong>${top}</strong>
              </div>
            `;
            topicsContainer.appendChild(lbl);
          });

          // 複訓與暫無規劃
          const extraOptions = [
            { val: "同一門課複習梯次（想再聽一次或推薦朋友）", emoji: "🔄" },
            { val: "暫無規劃（先吸收本次內容為主）", emoji: "🌱" }
          ];
          extraOptions.forEach(opt => {
            const lbl = document.createElement('label');
            lbl.className = 'radio-card compact';
            lbl.innerHTML = `
              <input type="radio" name="followup_interest_topic" value="${opt.val}">
              <div class="card-body">
                <span class="emoji">${opt.emoji}</span>
                <strong>${opt.val}</strong>
              </div>
            `;
            topicsContainer.appendChild(lbl);
          });
        }
      }
    }

    if (scheduleSection) {
      if (!isScheduleEnabled) {
        scheduleSection.style.display = 'none';
      } else {
        scheduleSection.style.display = 'block';
        const stepNumEl = document.getElementById('followupScheduleStepNum');
        if (stepNumEl) stepNumEl.textContent = String(currentStep).padStart(2, '0');
        currentStep++;

        // 動態渲染開課時段／課表晶片 (多選)
        const schedulesContainer = document.getElementById('followupSchedulesContainer');
        if (schedulesContainer) {
          schedulesContainer.innerHTML = '';
          const schedules = (data.followup_schedules && data.followup_schedules.length > 0)
            ? data.followup_schedules
            : [
                "🏛️【實體講座】11/15 (六) 14:00 - 16:00 台北站（實體面對面交流）",
                "🎨【實體單元課】11/22 (日) 13:30 - 16:30 台中教室精實班",
                "💻【線上直播班】12/01 起 每週三晚間 19:30 - 21:30"
              ];

          schedules.forEach(sch => {
            const item = document.createElement('label');
            item.className = 'radio-item';
            item.innerHTML = `
              <input type="checkbox" class="schedule-checkbox" value="${sch}" style="accent-color: var(--accent-primary); width: 17px; height: 17px;">
              <span style="font-size: 0.92rem; color: var(--text-primary); font-weight: 500;">${sch}</span>
            `;
            schedulesContainer.appendChild(item);
          });

          initScheduleCheckboxEvents();
        }
      }
    }

    if (rewardSection) {
      const rewardStepNum = rewardSection.querySelector('.step-num');
      if (rewardStepNum) {
        rewardStepNum.textContent = String(currentStep).padStart(2, '0');
      }
    }
  } catch (e) {
    console.log('Using default class configuration');
  }
}

// 課表多選與舊生早鳥折價券勾選互動邏輯
function initScheduleCheckboxEvents() {
  const scheduleCheckboxes = document.querySelectorAll('.schedule-checkbox');
  const offerAllChk = document.getElementById('followupOfferAllCheckbox');
  const notNeededChk = document.getElementById('followupNotNeededCheckbox');
  const hiddenInput = document.getElementById('followupSchedulesInput');

  function updateFollowupHiddenInput() {
    const selected = [];
    scheduleCheckboxes.forEach(cb => {
      if (cb.checked) selected.push(cb.value);
    });
    if (offerAllChk && offerAllChk.checked) {
      selected.push("🔥 願意接收舊生專屬早鳥優惠與開課通知");
    }
    if (notNeededChk && notNeededChk.checked) {
      selected.push("暫不需要");
    }
    if (hiddenInput) {
      hiddenInput.value = selected.join(" 、 ");
    }
  }

  scheduleCheckboxes.forEach(cb => {
    cb.addEventListener('change', () => {
      if (cb.checked && notNeededChk) {
        notNeededChk.checked = false;
      }
      updateFollowupHiddenInput();
    });
  });

  if (offerAllChk) {
    offerAllChk.addEventListener('change', () => {
      if (offerAllChk.checked && notNeededChk) {
        notNeededChk.checked = false;
      }
      updateFollowupHiddenInput();
    });
  }

  if (notNeededChk) {
    notNeededChk.addEventListener('change', () => {
      if (notNeededChk.checked) {
        scheduleCheckboxes.forEach(cb => { cb.checked = false; });
        if (offerAllChk) offerAllChk.checked = false;
      }
      updateFollowupHiddenInput();
    });
  }
}

// 初始化 NPS 評分刻度
function initNpsScale() {
  const container = document.getElementById('npsScale');
  const input = document.getElementById('nps_score_input');
  const display = document.getElementById('npsValDisplay');
  if (!container || !input) return;

  const defaultVal = 10;
  input.value = defaultVal;

  for (let i = 0; i <= 10; i++) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = `nps-btn ${i === defaultVal ? 'selected' : ''}`;
    btn.textContent = i;
    btn.dataset.val = i;

    btn.addEventListener('click', () => {
      container.querySelectorAll('.nps-btn').forEach(b => b.classList.remove('selected'));
      btn.classList.add('selected');
      input.value = i;
      
      let text = `${i} 分`;
      if (i >= 9) text += ' (強烈推薦 🔥)';
      else if (i >= 7) text += ' (滿意中立 👌)';
      else text += ' (有待改進 ⚠️)';
      display.textContent = text;
    });

    container.appendChild(btn);
  }
}

// 初始化星級評分
function initStarRatings() {
  const ratingGroups = document.querySelectorAll('.star-rating');
  const ratingDescriptions = {
    1: '非常不滿意 (1.0)',
    2: '不滿意 (2.0)',
    3: '普通一般 (3.0)',
    4: '滿意良好 (4.0)',
    5: '非常滿意 (5.0)'
  };

  ratingGroups.forEach(group => {
    const fieldName = group.dataset.name;
    const input = document.getElementById(`${fieldName}_input`);
    const textDisplay = document.getElementById(`${fieldName}_text`);
    const stars = group.querySelectorAll('.star-btn');

    updateStars(stars, 5);

    stars.forEach(star => {
      star.addEventListener('click', () => {
        const val = parseInt(star.dataset.val, 10);
        if (input) input.value = val;
        if (textDisplay) textDisplay.textContent = ratingDescriptions[val] || `${val}.0`;
        updateStars(stars, val);
      });
    });
  });

  function updateStars(stars, activeVal) {
    stars.forEach(s => {
      const v = parseInt(s.dataset.val, 10);
      if (v <= activeVal) {
        s.classList.add('active');
      } else {
        s.classList.remove('active');
      }
    });
  }
}

// 初始化多選標籤按鈕
function initTagSelectors() {
  setupTagSelector('progressTags', 'key_progress_input', 2);

  function setupTagSelector(containerId, inputId, maxAllowed) {
    const container = document.getElementById(containerId);
    const hiddenInput = document.getElementById(inputId);
    if (!container || !hiddenInput) return;

    const buttons = container.querySelectorAll('.tag-btn');
    const selectedValues = new Set();

    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const val = btn.dataset.value;
        if (selectedValues.has(val)) {
          selectedValues.delete(val);
          btn.classList.remove('selected');
        } else {
          if (maxAllowed && selectedValues.size >= maxAllowed) {
            alert(`此題最多可選擇 ${maxAllowed} 項喔！`);
            return;
          }
          selectedValues.add(val);
          btn.classList.add('selected');
        }
        hiddenInput.value = Array.from(selectedValues).join('、');
      });
    });
  }
}

// 根據後台好禮設定套用顯隱邏輯
function applyGiftVisibility() {
  const isGiftEnabled = (window.isGiftEnabled === true);
  const giftBanner = document.getElementById('heroGiftBanner');
  const q11 = document.getElementById('q11WantsRewardContainer');
  const rewardSection = document.getElementById('rewardRedemptionSection');
  const submitBtn = document.getElementById('submitBtn');
  const secNote = document.getElementById('securityNoteText');

  if (!isGiftEnabled) {
    if (giftBanner) giftBanner.style.display = 'none';
    if (q11) q11.style.display = 'none';
    if (rewardSection) rewardSection.style.display = 'none';

    // 自動勾選無需兌換好禮
    const noRadio = document.querySelector('input[name="wants_reward"][value="no"]');
    if (noRadio) noRadio.checked = true;

    // 移除第 05 區所有必填限制
    if (rewardSection) {
      const requiredFields = [
        'input[name="student_name"]',
        'input[name="phone"]',
        'input[name="privacy_agree"]'
      ];
      requiredFields.forEach(sel => {
        const el = rewardSection.querySelector(sel);
        if (el) el.removeAttribute('required');
      });
      const courseRadios = rewardSection.querySelectorAll('input[name="selected_reward_course"]');
      courseRadios.forEach(r => r.removeAttribute('required'));
    }

    if (submitBtn) {
      submitBtn.innerHTML = '<span>🚀 送出匿名結業回饋</span>';
    }
    if (secNote) {
      secNote.textContent = '🔒 我們嚴格保護您的回饋，資訊僅用於教學檢討與持續優化課程品質';
    }
  } else {
    if (giftBanner) giftBanner.style.display = 'flex';
    if (q11) q11.style.display = 'block';

    const wantsVal = document.querySelector('input[name="wants_reward"]:checked')?.value || 'yes';
    if (rewardSection) {
      rewardSection.style.display = (wantsVal === 'no') ? 'none' : 'block';
    }
    if (submitBtn) {
      submitBtn.innerHTML = (wantsVal === 'no') 
        ? '<span>🚀 送出結業回饋問卷</span>' 
        : '<span>🎁 登記兌換 ＆ 送出結業問卷</span>';
    }
    if (secNote) {
      secNote.textContent = '🔒 我們嚴格保護您的個資，資訊僅用於教學檢討與本次單元課兌換聯繫';
    }
  }
}

// 初始化是否兌換好禮之動態展開/折疊
function initRewardToggle() {
  const wantsRadios = document.querySelectorAll('input[name="wants_reward"]');
  const rewardSection = document.getElementById('rewardRedemptionSection');
  const submitBtn = document.getElementById('submitBtn');
  const yesLabel = document.getElementById('wantsYesLabel');
  const noLabel = document.getElementById('wantsNoLabel');
  
  if (!wantsRadios.length || !rewardSection) return;

  const requiredFields = [
    'input[name="student_name"]',
    'input[name="phone"]',
    'input[name="privacy_agree"]'
  ];

  function updateVisibility() {
    if (window.isGiftEnabled === false) {
      applyGiftVisibility();
      return;
    }

    const selectedVal = document.querySelector('input[name="wants_reward"]:checked')?.value || 'yes';
    if (selectedVal === 'no') {
      rewardSection.style.display = 'none';
      if (yesLabel) {
        yesLabel.style.borderColor = 'var(--border-color)';
        yesLabel.style.background = '#ffffff';
      }
      if (noLabel) {
        noLabel.style.borderColor = 'var(--accent-primary)';
        noLabel.style.background = 'var(--accent-soft)';
      }
      // 移除必填限制
      requiredFields.forEach(sel => {
        const el = rewardSection.querySelector(sel);
        if (el) el.removeAttribute('required');
      });
      const courseRadios = rewardSection.querySelectorAll('input[name="selected_reward_course"]');
      courseRadios.forEach(r => r.removeAttribute('required'));

      if (submitBtn) {
        submitBtn.innerHTML = '<span>🚀 送出結業回饋問卷</span>';
      }
    } else {
      rewardSection.style.display = 'block';
      if (yesLabel) {
        yesLabel.style.borderColor = 'var(--gold)';
        yesLabel.style.background = 'var(--gold-soft)';
      }
      if (noLabel) {
        noLabel.style.borderColor = 'var(--border-color)';
        noLabel.style.background = '#ffffff';
      }
      // 恢復必填限制 (姓名、電話、個資同意；LINE 與 Email 保持選填)
      requiredFields.forEach(sel => {
        const el = rewardSection.querySelector(sel);
        if (el) el.setAttribute('required', 'required');
      });
      const courseRadios = rewardSection.querySelectorAll('input[name="selected_reward_course"]');
      courseRadios.forEach(r => r.setAttribute('required', 'required'));

      if (submitBtn) {
        submitBtn.innerHTML = '<span>🎁 登記兌換 ＆ 送出結業問卷</span>';
      }
    }
  }

  wantsRadios.forEach(r => {
    r.addEventListener('change', updateVisibility);
  });
  updateVisibility();
}

// 初始化學習吃力/卡關「其他」自訂輸入框切換
function initStruggleOtherToggle() {
  const container = document.getElementById('strugglePointContainer');
  const otherWrap = document.getElementById('struggleOtherWrap');
  const otherInput = document.getElementById('struggleOtherText');
  if (!container || !otherWrap) return;

  const radios = container.querySelectorAll('input[name="struggle_point"]');
  radios.forEach(r => {
    r.addEventListener('change', () => {
      if (r.checked && r.value === '其他') {
        otherWrap.style.display = 'block';
        if (otherInput) otherInput.focus();
      } else if (r.checked) {
        otherWrap.style.display = 'none';
      }
    });
  });

  const checkedRadio = container.querySelector('input[name="struggle_point"]:checked');
  if (checkedRadio && checkedRadio.value === '其他') {
    otherWrap.style.display = 'block';
  } else {
    otherWrap.style.display = 'none';
  }
}

// 表單提交與好禮彈窗處理
function initFormSubmit() {
  const form = document.getElementById('surveyForm');
  const submitBtn = document.getElementById('submitBtn');
  const modal = document.getElementById('successModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalTitle = document.getElementById('modalTitle');
  const modalSub = document.getElementById('modalSub');
  const modalGiftBox = document.getElementById('modalGiftBox');
  const modalRewardCourseName = document.getElementById('modalRewardCourseName');

  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // 驗證 Q2 是否有選
    const keyProgress = document.getElementById('key_progress_input').value;
    if (!keyProgress) {
      alert('請在第 2 題選擇至少一項您最大的收穫進步喔！');
      document.getElementById('progressTags').scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    // 收集表單資料
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // 處理 Q3 「其他」卡關說明
    if (data.struggle_point === '其他') {
      const otherDetail = document.getElementById('struggleOtherText')?.value.trim();
      if (otherDetail) {
        data.struggle_point = `其他：${otherDetail}`;
      }
    }

    const isGiftEnabled = window.isGiftEnabled !== false;
    const wantsReward = isGiftEnabled && (data.wants_reward !== 'no');
    if (!wantsReward) {
      data.wants_reward = 'no';
      data.student_name = data.student_name || '匿名學員';
      data.selected_reward_course = isGiftEnabled ? '無需兌換好禮' : '未開放兌換 (純回饋模式)';
      data.phone = '';
      data.line_id = '';
      data.email = '';
    }

    if (!window.isFollowupTopicEnabled) {
      data.followup_interest_topic = "未開啟此項調查";
    } else {
      data.followup_interest_topic = data.followup_interest_topic || "未填寫";
    }

    if (!window.isFollowupScheduleEnabled) {
      data.followup_schedules_selected = "未開啟此項調查";
    } else {
      data.followup_schedules_selected = data.followup_schedules_selected || "未勾選時段";
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = wantsReward 
      ? '<span>🚀 兌換申請送出中...</span>' 
      : '<span>🚀 問卷送出中...</span>';

    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const result = await response.json();

      if (response.ok && result.status === 'success') {
        // 隱藏填寫表單，切換為完課感謝成功畫面 (學員絕不會再停留在已填寫的表單中)
        form.style.display = 'none';
        const completedCard = document.getElementById('surveyCompletedCard');
        const completedTitle = document.getElementById('completedTitle');
        const completedSub = document.getElementById('completedSub');
        const completedGiftBox = document.getElementById('completedGiftBox');
        const completedRewardCourseName = document.getElementById('completedRewardCourseName');

        if (!wantsReward) {
          if (modalTitle) modalTitle.textContent = '🎉 問卷回饋已成功送出！';
          if (modalSub) modalSub.textContent = '非常感謝您撥冗填寫寶貴意見，您的回饋將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalGiftBox) modalGiftBox.style.display = 'none';

          if (completedTitle) completedTitle.textContent = '🎉 問卷回饋已成功送出！';
          if (completedSub) completedSub.textContent = '非常感謝您撥冗填寫寶貴意見，您的回饋將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (completedGiftBox) completedGiftBox.style.display = 'none';
        } else {
          if (modalTitle) modalTitle.textContent = '🎉 問卷回饋與兌換申請已受理！';
          if (modalSub) modalSub.textContent = '感謝您的認真填寫，您的寶貴意見將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalGiftBox) modalGiftBox.style.display = 'block';
          if (modalRewardCourseName && data.selected_reward_course) {
            modalRewardCourseName.textContent = data.selected_reward_course;
          }

          if (completedTitle) completedTitle.textContent = '🎉 問卷回饋與兌換申請已受理！';
          if (completedSub) completedSub.textContent = '感謝您的認真填寫，您的寶貴意見將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (completedGiftBox) completedGiftBox.style.display = 'block';
          if (completedRewardCourseName && data.selected_reward_course) {
            completedRewardCourseName.textContent = data.selected_reward_course;
          }
        }

        if (completedCard) {
          completedCard.style.display = 'block';
        }
        window.scrollTo({ top: 0, behavior: 'smooth' });

        modal.classList.add('show');
      } else {
        alert(result.message || '提交時遇到問題，請再試一次！');
        submitBtn.disabled = false;
        submitBtn.innerHTML = wantsReward 
          ? '<span>🎁 登記兌換 ＆ 送出結業問卷</span>'
          : '<span>🚀 送出結業回饋問卷</span>';
      }
    } catch (err) {
      console.error('Submit error:', err);
      alert('⚠️ 送出時連線異常，請檢查網路連線後再試一次！\n錯誤訊息：' + err.message);
      submitBtn.disabled = false;
      submitBtn.innerHTML = wantsReward 
        ? '<span>🎁 登記兌換 ＆ 送出結業問卷</span>'
        : '<span>🚀 送出結業回饋問卷</span>';
    }
  });

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
      modal.classList.remove('show');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

// 供學員關閉問卷網頁
function handleCloseSurveyTab() {
  window.close();
  setTimeout(() => {
    alert('🎉 您已成功完成填答！請直接點擊手機瀏覽器左上角的「✕」或關閉分頁即可。');
  }, 250);
}
