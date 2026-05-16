/**
 * Barre type thermomètre pour la robustesse du mot de passe.
 * Zones : faible (rouge), moyen (orange), fort (vert).
 */
(function () {
  function scorePassword(pw) {
    if (!pw) return 0;
    let s = 0;
    if (pw.length >= 12) s += 28;
    else if (pw.length >= 8) s += 18;
    else s += Math.min(pw.length * 2, 14);

    if (/[a-z]/.test(pw)) s += 14;
    if (/[A-Z]/.test(pw)) s += 14;
    if (/[0-9]/.test(pw)) s += 14;
    if (/[^a-zA-Z0-9]/.test(pw)) s += 22;

    if (pw.length >= 16) s += 8;
    if (/[a-z]/.test(pw) && /[A-Z]/.test(pw) && /[0-9]/.test(pw) && /[^a-zA-Z0-9]/.test(pw)) s += 10;

    return Math.min(100, Math.round(s));
  }

  function stateForScore(score) {
    if (score === 0) return { cls: "state-none", labelCls: "text-muted-custom", text: "Saisissez un mot de passe" };
    if (score < 40) return { cls: "state-weak", labelCls: "text-weak", text: "Mot de passe fragile" };
    if (score < 70) return { cls: "state-medium", labelCls: "text-medium", text: "Mot de passe acceptable" };
    return { cls: "state-strong", labelCls: "text-strong", text: "Mot de passe robuste" };
  }

  function init(inputId, fillId, labelId) {
    var input = document.getElementById(inputId);
    var fill = document.getElementById(fillId);
    var label = document.getElementById(labelId);
    if (!input || !fill || !label) return;

    function update() {
      var score = scorePassword(input.value);
      var st = stateForScore(score);
      fill.className = "pwd-thermo-fill " + st.cls;
      fill.style.width = score + "%";
      label.className = "pwd-thermo-label " + st.labelCls;
      label.textContent = st.text;
    }

    input.addEventListener("input", update);
    input.addEventListener("focus", update);
    update();
  }

  document.addEventListener("DOMContentLoaded", function () {
    init("id_password1", "pwd-thermo-fill", "pwd-thermo-label");
  });
})();
