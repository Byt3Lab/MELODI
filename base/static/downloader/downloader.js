/**
 * Downloader class to handle file downloads using anchor tags or fetch API.
 */
export default class Downloader {
    /**
     * Downloads a resource using a temporary anchor element.
     * Automatically falls back to fetch for cross-origin URLs to ensure direct download.
     * 
     * @param {string} url - The URL of the resource to download.
     * @param {string} filename - The name to save the file as.
     */
    static async downloadViaAnchor(url, filename = '') {
        // Check if the URL is cross-origin
        const isCrossOrigin = (url) => {
            try {
                const target = new URL(url, window.location.origin);
                return target.origin !== window.location.origin;
            } catch (e) {
                return false;
            }
        };

        if (isCrossOrigin(url)) {
            console.warn('Cross-origin URL detected. Falling back to fetch for direct download.');
            await this.downloadViaFetch(url, filename);
            return;
        }

        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = filename;
        anchor.style.display = 'none';
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    }

    /**
     * Downloads a resource using the fetch API.
     * Best for resources that require headers or for tracking progress.
     * 
     * @param {string} url - The URL of the resource to download.
     * @param {string} filename - The name to save the file as.
     * @param {Object} options - Fetch API options (headers, method, etc.).
     * @returns {Promise<void>}
     */
    static async downloadViaFetch(url, filename = '', options = {}) {
        try {
            const response = await fetch(url, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const blob = await response.blob();
            const blobUrl = URL.createObjectURL(blob);

            await this.downloadViaAnchor(blobUrl, filename);

            // Cleanup the object URL after a short delay
            setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
        } catch (error) {
            console.error('Download failed:', error);
            throw error;
        }
    }
}