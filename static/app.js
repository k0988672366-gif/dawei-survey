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

    // 判斷是否開啟學員個資收集 (預設為 true，關閉則為 100% 全匿名問卷)
    window.isContactCollectionEnabled = (data.enable_contact !== false);

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

    if (pill1El) pill1El.textContent = data.pill_1 || '⏱ 只需 1 分鐘';
    if (pill2El) pill2El.textContent = data.pill_2 || '📋 課綱痛點健檢';
    if (pill3El) pill3El.textContent = data.pill_3 || '🛡 資料僅供教學';

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

    // 獨立處理 13. 即將開課課表
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
          topicQuestionLabel.innerHTML = `未來若由【${teacherName}老師】或團隊開設進階延伸主題，您是否有興趣繼續深入學習？ <small class="hint">（可協助教學團隊規劃後續梯次大綱）</small>`;
        }

        // 綁定 是／否／目前沒想法，可專員聯繫 互動事件
        const choiceRadios = document.querySelectorAll('input[name="followup_interest_choice"]');
        const customTopicWrap = document.getElementById('followupCustomTopicWrap');
        const customTopicInput = document.getElementById('followupCustomTopicInput');
        const yesLbl = document.getElementById('topicYesLabel');
        const noLbl = document.getElementById('topicNoLabel');
        const contactLbl = document.getElementById('topicContactLabel');

        function updateChoiceStyle() {
          const checkedVal = document.querySelector('input[name="followup_interest_choice"]:checked')?.value;
          if (yesLbl) {
            yesLbl.style.borderColor = (checkedVal === 'yes') ? 'var(--accent-primary)' : 'var(--border-color)';
            yesLbl.style.background = (checkedVal === 'yes') ? 'var(--accent-soft)' : '#ffffff';
          }
          if (noLbl) {
            noLbl.style.borderColor = (checkedVal === 'no') ? 'var(--border-color)' : 'var(--border-color)';
            noLbl.style.background = (checkedVal === 'no') ? '#f8fafc' : '#ffffff';
          }
          if (contactLbl) {
            contactLbl.style.borderColor = (checkedVal === 'contact') ? 'var(--accent-primary)' : 'var(--border-color)';
            contactLbl.style.background = (checkedVal === 'contact') ? 'var(--accent-soft)' : '#ffffff';
          }

          if (customTopicWrap) {
            if (checkedVal === 'yes') {
              customTopicWrap.style.display = 'block';
              if (customTopicInput) customTopicInput.focus();
            } else {
              customTopicWrap.style.display = 'none';
            }
          }

          // 即時連動更新聯絡資訊區塊顯隱 (若勾選 是 或 可專員聯繫 即智慧展開個資)
          updateDynamicContactVisibility();
        }

        choiceRadios.forEach(r => {
          r.addEventListener('change', updateChoiceStyle);
        });
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

        // 動態渲染開課時段／課表晶片 (僅線上直播班時段)
        const schedulesContainer = document.getElementById('followupSchedulesContainer');
        if (schedulesContainer) {
          schedulesContainer.innerHTML = '';
          const schedules = (data.followup_schedules && data.followup_schedules.length > 0)
            ? data.followup_schedules
            : [
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

    // 智能動態聯絡資料顯隱與必填規則初始化
    updateDynamicContactVisibility();
  } catch (e) {
    console.log('Using default class configuration');
  }
}

// 課表多選勾選互動邏輯
function initScheduleCheckboxEvents() {
  const scheduleCheckboxes = document.querySelectorAll('.schedule-checkbox');
  const hiddenInput = document.getElementById('followupSchedulesInput');

  function updateFollowupHiddenInput() {
    const selected = [];
    scheduleCheckboxes.forEach(cb => {
      if (cb.checked) selected.push(cb.value);
    });
    if (hiddenInput) {
      hiddenInput.value = selected.join(" 、 ");
    }
    if (typeof updateDynamicContactVisibility === 'function') {
      updateDynamicContactVisibility();
    }
  }

  scheduleCheckboxes.forEach(cb => {
    cb.addEventListener('change', updateFollowupHiddenInput);
  });
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

// 全域動態聯絡資訊與序號排版控制器 (智能模式)
function updateDynamicContactVisibility() {
  const isGiftEnabled = (window.isGiftEnabled === true);
  const giftBanner = document.getElementById('heroGiftBanner');
  const q11 = document.getElementById('q11WantsRewardContainer');
  const rewardSection = document.getElementById('rewardRedemptionSection');
  const contactSection = document.getElementById('contactInfoSection');
  const contactTitle = document.getElementById('contactSectionTitle');
  const contactReminder = document.getElementById('contactSectionReminder');
  const submitBtn = document.getElementById('submitBtn');
  const secNote = document.getElementById('securityNoteText');

  const studentNameInput = document.getElementById('studentNameInput');
  const studentPhoneInput = document.getElementById('studentPhoneInput');
  const studentLineInput = document.getElementById('studentLineInput');
  const privacyAgreeCheckbox = document.getElementById('privacyAgreeCheckbox');
  const nameReqMark = document.getElementById('nameReqMark');
  const phoneReqMark = document.getElementById('phoneReqMark');
  const lineReqMark = document.getElementById('lineReqMark');

  // 1. 好禮橫幅與 Q11 意願按鈕顯隱
  if (giftBanner) giftBanner.style.display = isGiftEnabled ? 'flex' : 'none';
  if (q11) q11.style.display = isGiftEnabled ? 'block' : 'none';

  // 2. 好禮單元課清單顯隱
  const wantsRewardVal = isGiftEnabled ? (document.querySelector('input[name="wants_reward"]:checked')?.value || 'yes') : 'no';
  const hasRewardInterest = isGiftEnabled && (wantsRewardVal !== 'no');
  if (rewardSection) {
    rewardSection.style.display = hasRewardInterest ? 'block' : 'none';
    const courseRadios = rewardSection.querySelectorAll('input[name="selected_reward_course"]');
    courseRadios.forEach(r => {
      if (hasRewardInterest) r.setAttribute('required', 'required');
      else r.removeAttribute('required');
    });
  }

  // 3. 判斷 12. 延伸進階主題是否有勾選需要深入學習或聯繫 (是 / 目前沒想法，可專員聯繫)
  let hasTopicInterest = false;
  if (window.isFollowupTopicEnabled) {
    const checkedTopicChoice = document.querySelector('input[name="followup_interest_choice"]:checked')?.value;
    if (checkedTopicChoice === 'yes' || checkedTopicChoice === 'contact') {
      hasTopicInterest = true;
    }
  }

  // 4. 判斷 13. 即將開課課表是否有勾選 (勾選直播時段)
  let hasScheduleInterest = false;
  if (window.isFollowupScheduleEnabled) {
    const checkedSchedules = document.querySelectorAll('.schedule-checkbox:checked');
    if (checkedSchedules && checkedSchedules.length > 0) {
      hasScheduleInterest = true;
    }
  }

  // 5. 雙層智慧連動邏輯（與後台設定不衝突）：
  // (A) 後台勾選「需留個資 / 強制留個資」時：所有人一律強制留個資
  // (B) 後台未勾選「需留個資」（預設純匿名問卷）時：若學員主動選了「好禮兌換」、「延伸學習(是/專員聯繫)」或「開課時段/早鳥通知」，自動智慧彈性展開個資填寫區！
  const isBackendContactMandatory = (window.isContactCollectionEnabled !== false);
  const hasStudentRequestedFollowup = (hasRewardInterest || hasTopicInterest || hasScheduleInterest);
  const shouldRequireContact = isBackendContactMandatory || hasStudentRequestedFollowup;
  window.isContactRequired = shouldRequireContact;

  if (contactSection) {
    if (!shouldRequireContact) {
      // 100% 全匿名問卷：學員未勾選好禮、未勾選時段、未要求專員聯繫，且後台未強制留個資
      contactSection.style.display = 'none';

      // 移除必填限制並清空欄位
      if (studentNameInput) {
        studentNameInput.removeAttribute('required');
        studentNameInput.value = '';
      }
      if (studentPhoneInput) {
        studentPhoneInput.removeAttribute('required');
        studentPhoneInput.value = '';
      }
      if (studentLineInput) {
        studentLineInput.removeAttribute('required');
        studentLineInput.value = '';
      }
      const studentEmailInput = document.getElementById('studentEmailInput');
      if (studentEmailInput) {
        studentEmailInput.removeAttribute('required');
        studentEmailInput.value = '';
      }
      if (privacyAgreeCheckbox) privacyAgreeCheckbox.removeAttribute('required');

      if (submitBtn) submitBtn.innerHTML = '<span>🚀 送出匿名結業回饋</span>';
      if (secNote) {
        secNote.textContent = '🔒 本問卷為 100% 匿名填答，無須填寫任何個人資料，請安心表達真實感受';
      }
    } else {
      // 需留個資（後台強制 或 學員主動預約聯繫/時段/好禮）
      contactSection.style.display = 'block';

      // 設置必填 (姓名、手機、個資同意必填；LINE ID 與 Email 為非必填)
      if (studentNameInput) studentNameInput.setAttribute('required', 'required');
      if (studentPhoneInput) studentPhoneInput.setAttribute('required', 'required');
      if (studentLineInput) studentLineInput.removeAttribute('required');
      const studentEmailInput = document.getElementById('studentEmailInput');
      if (studentEmailInput) studentEmailInput.removeAttribute('required');
      if (privacyAgreeCheckbox) privacyAgreeCheckbox.setAttribute('required', 'required');

      if (nameReqMark) nameReqMark.style.display = 'inline';
      if (phoneReqMark) phoneReqMark.style.display = 'inline';
      if (lineReqMark) lineReqMark.style.display = 'none';

      // 依情境切換文案與提交按鈕
      if (hasRewardInterest) {
        if (contactTitle) contactTitle.innerHTML = '🎁 登記單元課兌換 ＆ 學員聯絡資訊';
        if (contactReminder) {
          contactReminder.innerHTML = '📞 <strong>學員聯絡資料填寫</strong>：請填寫您的稱呼與聯絡電話（LINE ID 與 Email 為選填），專員將於 1~2 工作天內主動聯繫為您開通所選線上單元課！';
        }
        if (submitBtn) submitBtn.innerHTML = '<span>🎁 登記兌換 ＆ 送出結業問卷</span>';
      } else if (hasScheduleInterest) {
        if (contactTitle) contactTitle.innerHTML = '📮 接收開課課表通知 ＆ 學員聯絡資訊';
        if (contactReminder) {
          contactReminder.innerHTML = '📞 <strong>開課梯次通知</strong>：請填寫正確的手機號碼（LINE ID 與 Email 為選填），開課前專員將在第一時間優先為您傳送【最新開課梯次與課表時段資訊】！';
        }
        if (submitBtn) submitBtn.innerHTML = '<span>🚀 預約開課時段 ＆ 送出結業問卷</span>';
      } else if (hasTopicInterest) {
        if (contactTitle) contactTitle.innerHTML = '📮 接收進階主題開課通知 ＆ 學員聯絡資訊';
        if (contactReminder) {
          contactReminder.innerHTML = '📞 <strong>新課梯次優先通知</strong>：請填寫您的稱呼與聯絡電話（LINE ID 與 Email 為選填），後續若開設您感興趣的進階延伸主題，專員將在第一時間為您發送開課資訊！';
        }
        if (submitBtn) submitBtn.innerHTML = '<span>🚀 登記新課通知 ＆ 送出結業問卷</span>';
      } else {
        if (contactTitle) contactTitle.innerHTML = '📮 學員聯絡資訊';
        if (contactReminder) {
          contactReminder.innerHTML = '📞 <strong>學員聯絡資料填寫</strong>：請填寫您的稱呼與聯絡電話（LINE ID 與 Email 為選填），以便教學團隊為您建立學員檔案、開通線上服務或發送課後資訊！';
        }
        if (submitBtn) submitBtn.innerHTML = '<span>🚀 送出結業回饋問卷</span>';
      }
      if (secNote) {
        secNote.textContent = '🔒 我們嚴格保護您的個資，資訊僅用於教學檢討、聯繫開通與開課資訊通知';
      }
    }
  }

  // 6. 動態自適應更新所有區塊之 step-num 序號
  updateAllSectionStepNumbers();
}

function updateAllSectionStepNumbers() {
  let step = 5;
  const topicSec = document.getElementById('followupTopicSection');
  if (topicSec && topicSec.style.display !== 'none') {
    const el = document.getElementById('followupTopicStepNum');
    if (el) el.textContent = String(step++).padStart(2, '0');
  }

  const schSec = document.getElementById('followupScheduleSection');
  if (schSec && schSec.style.display !== 'none') {
    const el = document.getElementById('followupScheduleStepNum');
    if (el) el.textContent = String(step++).padStart(2, '0');
  }

  const rewardSec = document.getElementById('rewardRedemptionSection');
  if (rewardSec && rewardSec.style.display !== 'none') {
    const el = document.getElementById('rewardStepNum') || rewardSec.querySelector('.step-num');
    if (el) el.textContent = String(step++).padStart(2, '0');
  }

  const contactSec = document.getElementById('contactInfoSection');
  if (contactSec && contactSec.style.display !== 'none') {
    const el = document.getElementById('contactStepNum');
    if (el) el.textContent = String(step++).padStart(2, '0');
  }
}

// 根據後台好禮設定套用顯隱邏輯
function applyGiftVisibility() {
  updateDynamicContactVisibility();
}

// 初始化是否兌換好禮之動態展開/折疊
function initRewardToggle() {
  const wantsRadios = document.querySelectorAll('input[name="wants_reward"]');
  const yesLabel = document.getElementById('wantsYesLabel');
  const noLabel = document.getElementById('wantsNoLabel');
  
  if (!wantsRadios.length) return;

  function updateCardsStyle() {
    const selectedVal = document.querySelector('input[name="wants_reward"]:checked')?.value || 'yes';
    if (yesLabel) {
      yesLabel.style.borderColor = (selectedVal === 'yes') ? 'var(--gold)' : 'var(--border-color)';
      yesLabel.style.background = (selectedVal === 'yes') ? 'var(--gold-soft)' : '#ffffff';
    }
    if (noLabel) {
      noLabel.style.borderColor = (selectedVal === 'no') ? 'var(--accent-primary)' : 'var(--border-color)';
      noLabel.style.background = (selectedVal === 'no') ? 'var(--accent-soft)' : '#ffffff';
    }
    updateDynamicContactVisibility();
  }

  wantsRadios.forEach(r => {
    r.addEventListener('change', updateCardsStyle);
  });
  updateCardsStyle();
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

    // 處理「💬 我想要說」文字框 (選填 / 不強制填寫)
    const feedbackInput = document.getElementById('feedbackTextInput');
    if (feedbackInput && feedbackInput.value.trim()) {
      data.feedback_text = feedbackInput.value.trim();
    } else {
      data.feedback_text = (data.feedback_text || '').trim();
    }

    const isGiftEnabled = window.isGiftEnabled === true;
    const wantsReward = isGiftEnabled && (data.wants_reward !== 'no');
    const isContactRequired = window.isContactRequired === true;

    if (!wantsReward) {
      data.wants_reward = 'no';
      data.selected_reward_course = isGiftEnabled ? '無需兌換好禮' : '未開放兌換 (純回饋模式)';
    }

    if (!isContactRequired) {
      data.student_name = '匿名學員';
      data.phone = '';
      data.line_id = '';
      data.email = '';
    } else {
      data.student_name = data.student_name ? data.student_name.trim() : '學員';
      data.phone = data.phone ? data.phone.trim() : '';
      data.line_id = data.line_id ? data.line_id.trim() : '';
      data.email = data.email ? data.email.trim() : '';
    }

    // 處理 12. 延伸進階主題意願 (是 / 否 / 目前沒想法，可專員聯繫)
    if (!window.isFollowupTopicEnabled) {
      data.followup_interest_topic = "未開啟此項調查";
    } else {
      const choice = document.querySelector('input[name="followup_interest_choice"]:checked')?.value;
      const customTopic = document.getElementById('followupCustomTopicInput')?.value.trim();
      if (choice === 'yes') {
        data.followup_interest_topic = customTopic ? `是：${customTopic}` : '是（未填寫具體內容）';
      } else if (choice === 'no') {
        data.followup_interest_topic = '否，目前暫無規劃';
      } else if (choice === 'contact') {
        data.followup_interest_topic = '目前沒想法，可專員聯繫';
      } else {
        data.followup_interest_topic = data.followup_interest_topic || '未勾選';
      }
    }

    if (!window.isFollowupScheduleEnabled) {
      data.followup_schedules_selected = "未開啟此項調查";
    } else {
      data.followup_schedules_selected = data.followup_schedules_selected || "未勾選時段";
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = wantsReward 
      ? '<span>🚀 兌換申請送出中...</span>' 
      : (isContactRequired ? '<span>🚀 問卷送出中...</span>' : '<span>🚀 匿名問卷送出中...</span>');

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

        if (wantsReward) {
          const t = '🎉 問卷回饋與兌換申請已受理！';
          const s = '感謝您的認真填寫，您的寶貴意見將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalTitle) modalTitle.textContent = t;
          if (modalSub) modalSub.textContent = s;
          if (modalGiftBox) modalGiftBox.style.display = 'block';
          if (modalRewardCourseName && data.selected_reward_course) {
            modalRewardCourseName.textContent = data.selected_reward_course;
          }
          if (completedTitle) completedTitle.textContent = t;
          if (completedSub) completedSub.textContent = s;
          if (completedGiftBox) completedGiftBox.style.display = 'block';
          if (completedRewardCourseName && data.selected_reward_course) {
            completedRewardCourseName.textContent = data.selected_reward_course;
          }
        } else if (isContactRequired) {
          const t = '🎉 結業問卷已成功送出！';
          const s = '非常感謝您撥冗填寫寶貴意見，您的回饋將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalTitle) modalTitle.textContent = t;
          if (modalSub) modalSub.textContent = s;
          if (modalGiftBox) modalGiftBox.style.display = 'none';
          if (completedTitle) completedTitle.textContent = t;
          if (completedSub) completedSub.textContent = s;
          if (completedGiftBox) completedGiftBox.style.display = 'none';
        } else {
          const t = '🎉 匿名結業問卷已成功送出！';
          const s = '非常感謝您撥冗填寫寶貴意見，您的回饋將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalTitle) modalTitle.textContent = t;
          if (modalSub) modalSub.textContent = s;
          if (modalGiftBox) modalGiftBox.style.display = 'none';
          if (completedTitle) completedTitle.textContent = t;
          if (completedSub) completedSub.textContent = s;
          if (completedGiftBox) completedGiftBox.style.display = 'none';
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
