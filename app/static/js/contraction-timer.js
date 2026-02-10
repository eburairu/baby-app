/**
 * 陣痛タイマー クライアント側スクリプト
 * リアルタイムでタイマー表示を更新
 */

class ContractionTimer {
    constructor(startTimeISO) {
        this.startTime = new Date(startTimeISO);
        this.timerElement = document.getElementById('timer-display');
        this.intervalId = null;
    }

    start() {
        if (this.intervalId) {
            return; // 既に開始している場合は何もしない
        }

        // 初回表示
        this.update();

        // 1秒ごとに更新
        this.intervalId = setInterval(() => {
            this.update();
        }, 1000);
    }

    update() {
        if (!this.timerElement) {
            this.stop();
            return;
        }

        const now = new Date();
        const diffSeconds = Math.floor((now - this.startTime) / 1000);

        const minutes = Math.floor(diffSeconds / 60);
        const seconds = diffSeconds % 60;

        this.timerElement.textContent =
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    stop() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }
}

// グローバルタイマーインスタンス
window.contractionTimer = null;

// タイマー開始関数（HTMLから呼び出し可能）
function startContractionTimer(startTimeISO) {
    if (window.contractionTimer) {
        window.contractionTimer.stop();
    }

    window.contractionTimer = new ContractionTimer(startTimeISO);
    window.contractionTimer.start();
}

// ページアンロード時にタイマーを停止
window.addEventListener('beforeunload', () => {
    if (window.contractionTimer) {
        window.contractionTimer.stop();
    }
});
