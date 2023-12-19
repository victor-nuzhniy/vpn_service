function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

const domain = getCookie("user_domain")
function changeLinks(){
    links = document.getElementsByTagName("a");
    for(const link of links){
        if(link.href.includes("http") && !link.href.includes("localhost") && link.href.includes(domain)){
            const linkList = link.href.split("//")
            link.href = "http://" + location.host + "/localhost/" + linkList[1]
        } else if(!link.href.includes("http")){
            link.href = "http://" + location.host + "/localhost" + link.href
        };
    };
    forms = document.getElementsByTagName("form")
    for(const form in forms){
        if(Boolean(form.action)){
            if(form.action.includes("http") && !form.action.includes("localhost") && form.action.includes(domain)){
                const formList = form.action.split("//");
                form.action = "http://" + location.host + "/localhost/" + formList[1]
            } else if(!form.action.includes("http")){
                form.action = "http://" + location.host + "/localhost" + form.action
            };
        };
    };
};
changeLinks()
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

var observer = new MutationObserver(function(mutations, observer) {
    changeLinks()
});

observer.observe(document, {
  childList: true
});