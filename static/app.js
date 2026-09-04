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

  try {
    const reqUrl = classId ? `/api/class-info?class_id=${classId}` : '/api/class-info';
    const res = await fetch(reqUrl);
    if (!res.ok) return;
    const data = await res.json();
    if (document.getElementById('classIdInput')) {
      document.getElementById('classIdInput').value = data.class_id || classId || 'default';
    }

    // 更新頂部卡片所有文案
    if (data.badge_text && document.getElementById('badgeText')) {
      document.getElementById('badgeText').textContent = data.badge_text;
    }
    if (data.course_name && document.getElementById('courseTitle')) {
      document.getElementById('courseTitle').textContent = data.course_name;
      document.title = `${data.course_name} 結業回饋＆線上單元課兌換`;
    }
    if (data.course_subtitle && document.getElementById('courseSubtitle')) {
      document.getElementById('courseSubtitle').textContent = data.course_subtitle;
    }
    if (data.gift_banner_title && document.getElementById('giftBannerTitle')) {
      document.getElementById('giftBannerTitle').textContent = data.gift_banner_title;
    }
    if (data.gift_banner_desc && document.getElementById('giftBannerDesc')) {
      document.getElementById('giftBannerDesc').textContent = data.gift_banner_desc;
    }
    if (data.pill_1 && document.getElementById('pill1')) {
      document.getElementById('pill1').textContent = data.pill_1;
    }
    if (data.pill_2 && document.getElementById('pill2')) {
      document.getElementById('pill2').textContent = data.pill_2;
    }
    if (data.pill_3 && document.getElementById('pill3')) {
      document.getElementById('pill3').textContent = data.pill_3;
    }
    if (data.teacher_name) {
      document.querySelectorAll('.teacher-name-span').forEach(el => {
        el.textContent = `${data.teacher_name}老師`;
      });
    }

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
          chip.style.cssText = 'background: rgba(99, 102, 241, 0.12); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 6px; padding: 3px 8px; font-size: 0.78rem;';
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
  } catch (e) {
    console.log('Using default class configuration');
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
    const selectedVal = document.querySelector('input[name="wants_reward"]:checked')?.value || 'yes';
    if (selectedVal === 'no') {
      rewardSection.style.display = 'none';
      if (yesLabel) {
        yesLabel.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        yesLabel.style.background = 'rgba(255, 255, 255, 0.03)';
      }
      if (noLabel) {
        noLabel.style.borderColor = 'rgba(99, 102, 241, 0.6)';
        noLabel.style.background = 'rgba(99, 102, 241, 0.15)';
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
        yesLabel.style.borderColor = 'rgba(245, 158, 11, 0.5)';
        yesLabel.style.background = 'rgba(245, 158, 11, 0.08)';
      }
      if (noLabel) {
        noLabel.style.borderColor = 'rgba(255, 255, 255, 0.12)';
        noLabel.style.background = 'rgba(255, 255, 255, 0.03)';
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

    const wantsReward = data.wants_reward !== 'no';
    if (!wantsReward) {
      data.student_name = data.student_name || '匿名學員';
      data.selected_reward_course = '無需兌換好禮';
      data.phone = '';
      data.line_id = '';
      data.email = '';
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
        if (!wantsReward) {
          if (modalTitle) modalTitle.textContent = '🎉 問卷回饋已成功送出！';
          if (modalSub) modalSub.textContent = '非常感謝您撥冗填寫寶貴意見，您的回饋將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalGiftBox) modalGiftBox.style.display = 'none';
        } else {
          if (modalTitle) modalTitle.textContent = '🎉 問卷回饋與兌換申請已受理！';
          if (modalSub) modalSub.textContent = '感謝您的認真填寫，您的寶貴意見將幫助教學團隊持續打磨更好的學習體驗 ✨';
          if (modalGiftBox) modalGiftBox.style.display = 'block';
          if (modalRewardCourseName && data.selected_reward_course) {
            modalRewardCourseName.textContent = data.selected_reward_course;
          }
        }
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
      modal.classList.add('show');
    }
  });

  if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => {
      modal.classList.remove('show');
    });
  }
}
