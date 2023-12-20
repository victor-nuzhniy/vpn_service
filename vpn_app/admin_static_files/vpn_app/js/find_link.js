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
            link.href = "http://" + location.host + "/localhost/" + domain + link.href
        };
    };
    forms = document.getElementsByTagName("form")
    for(const form in forms){
        if(Boolean(form.action)){
            if(form.action.includes("http") && !form.action.includes("localhost") && form.action.includes(domain)){
                const formList = form.action.split("//");
                form.action = "http://" + location.host + "/localhost/" + formList[1]
            } else if(!form.action.includes("http")){
                form.action = "http://" + location.host + "/localhost/" + domain + form.action
            };
        };
    };
    scripts = document.getElementsByTagName("script")
    for(const script of scripts){
        if(Boolean(script.src)){
            if(script.src.includes("http") && !script.src.includes("localhost") && script.src.includes(domain)){
                const scriptList=script.src.split("//");
                script.src = "http://" + location.host + "/localhost/" + scriptList[1]
            } else if(!script.src.includes("http")) {
                script.src = "http://" + location.host + "/localhost" + + domain + script.src
            } else if(script.src.includes("http") && !script.src.includes("localhost") && script.src.includes(location.host)){
                const scriptList = script.src.split(location.host);
                script.src = "http://" + location.host + "/localhost/" + domain + scriptList[1]
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

const body = document.getElementsByTagName("body");

const config = { attributes: true, childList: true, subtree: true };

const callback = (mutationList, observer) => {
  for (const mutation of mutationList) {
    if (mutation.type === "childList") {
      changeLinks();
    };
  };
};

const observer = new MutationObserver(callback);

if(Boolean(body)){
    const config = {childList: true};
    observer.observe(body[0], config);
    observer.disconnect();
}
