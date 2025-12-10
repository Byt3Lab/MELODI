(function () {
    let mljs = {};

    class Modal {
        constructor(modalId) {
            this.modalElement = document.getElementById(modalId);
        }

        show() {
        }

        close() {
        }
    }

    class Alert {
        constructor(id='mljsAlertPlaceholder') {
            this.message = message;
            this.type = type;
            this.id = id;
            this.el = document.getElementById(id);
        }

        show(message, type="info") {
            const alertPlaceholder = this.el;
            const wrapper = document.createElement('div');
            wrapper.innerHTML = `
                <div class="alert alert-${type} alert-dismissible" role="alert">
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `;
            alertPlaceholder.append(wrapper);
        }

        clear() {
            const alertPlaceholder = this.el;
            alertPlaceholder.innerHTML = '';
        }
    }

    class Carousel {
        constructor(carouselId) {
            this.carouselElement = document.getElementById(carouselId);
        }

        next() {
        }

        prev() {
        }
    }

    function onBeforeLeavePage(callback) {
        window.addEventListener("beforeunload", function (e) {
            function alertUser(message) {
                e.preventDefault();
                e.returnValue = message;
                return message; 
            }

            callback(alertUser);
        });

        // Utilisation : appeler cette fonction lorsque l'utilisateur a des modifications non enregistrées
        // callbackFunction((alertUser)=>{if(condition){alertUser()}})
        // warnBeforeLeavePage(callbackFunction);
    }

    mljs.Alert = Alert;
    mljs.Modal = Modal;
    mljs.Carousel = Carousel;
    mljs.onBeforeLeavePage = onBeforeLeavePage;
    window.mljs = mljs
})()