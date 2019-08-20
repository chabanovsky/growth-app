var strings = {
    en: {
        welcome: 'Welcome!',
        mouseOver: 'Mouse over the community in your language to change the language or click on it to login.',
        firstBelieve: 'We believe that the desire to share knowledge with colleagues is not related to the language we speak, it is part of human nature.',
        secondBelieve: 'We believe that there are many among us who would like to help colleagues with advice in English.',
        thirdBelieve: 'We believe that leading by example, we encourage other talented developers do the same.',
        together: 'We are glad to everyone who wants to grow a English-speaking developer community. Together we will build the best software developer community of mutual help in the English language.',
        join: 'Click to login'
    },
    ru: {
        welcome: 'Здравствуйте!',
        mouseOver: 'Наведите мышкой на сообщество на вашем языке, чтобы изменить язык или нажмите на него, чтобы войти.',
        firstBelieve: 'Мы верим, что желание делиться знаниями с коллегами не связано с языком, на котором мы говорим, оно часть природы человека.',
        secondBelieve: 'Мы верим, что среди нас много тех, кто с радостью поможет коллегам советом на русском языке.',
        thirdBelieve: 'Мы верим, что своим примером, мы увлечем за собой других талантливых разработчиков.',
        together: 'Рады всем, кто хочет развивать русскоязычное сообщество программистов. Вместе мы создадим лучшее сообщество взаимной помощи по программированию на русском языке.',
        join: 'Нажмите, чтобы войти'
    },
    es: {
        welcome: 'Welcome!',
        mouseOver: 'Mouse over the community in your language to change the language or click on it to login.',
        firstBelieve: 'We believe that the desire to share knowledge with colleagues is not related to the language we speak, it is part of human nature.',
        secondBelieve: 'We believe that there are many among us who would like to help colleagues with advice in Spanish.',
        thirdBelieve: 'We believe that leading by example, we encourage other talented developers do the same.',
        together: 'We are glad to  everyone who wants to grow a Spanish-speaking developer community. Together we will build the best software developer community of mutual help in the Spanish language.',
        join: 'Click to login'
    },
    pt: {
        welcome: 'Welcome!',
        mouseOver: 'Mouse over the community in your language to change the language or click on it to login.',
        firstBelieve: 'We believe that the desire to share knowledge with colleagues is not related to the language we speak, it is part of human nature.',
        secondBelieve: 'We believe that there are many among us who would like to help colleagues with advice in Portuguese.',
        thirdBelieve: 'We believe that leading by example, we encourage other talented developers do the same.',
        together: 'We are glad to everyone who wants to grow a Portuguese-speaking developer community. Together we will build the best software developer community of mutual help in the Portuguese language.',
        join:'Click to login'
    },
    ja: {
        welcome: 'Welcome!',
        mouseOver: 'Mouse over the community in your language to change the language or click on it to login.',
        firstBelieve: 'We believe that the desire to share knowledge with colleagues is not related to the language we speak, it is part of human nature.',
        secondBelieve: 'We believe that there are many among us who would like to help colleagues with advice in Japanese.',
        thirdBelieve: 'We believe that leading by example, we encourage other talented developers do the same.',
        together: 'We are glad to everyone who wants to grow a Japanese-speaking developer community. Together we will build the best software developer community of mutual help in the Japanese language.',
        join: 'Click to login'
    }
}

var welcomeTag      = "#welcome";
var langHintTag     = "#lang-hint";
var firstBelieveTag = "#first-believe";
var secondBelieveTag= "#second-believe";
var thirdBelieveTag = "#third-believe";
var togetherTag     = "#together";
var joinTag         = "#join";
var currentLanguage;

$(document).ready(function() {
    changeLanguage("en");
    $("#communities a").mouseover(function(event){
        url = event.target.parentElement.href
        language = $.urlParam (url, "language");
        changeLanguage(language);
    });
    $(joinTag).click(function(event){
        event.preventDefault();
        url = event.target.href;
        url = url + "?language=" + currentLanguage;
        window.location.href = url;
    });
});

function changeLanguage(language) {
    currentLanguage = language;
    str = strings[language];
    $(welcomeTag).text(str.welcome);
    $(langHintTag).text(str.mouseOver);
    $(firstBelieveTag).text(str.firstBelieve);
    $(secondBelieveTag).text(str.secondBelieve);
    $(thirdBelieveTag).text(str.thirdBelieve);
    $(togetherTag).text(str.together);
    $(joinTag).text(str.join);
}

// For more information look at https://stackoverflow.com/q/19491336/564240
$.urlParam = function(url, name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(url);
    if (results==null) {
       return null;
    }
    return decodeURI(results[1]) || 0;
}
