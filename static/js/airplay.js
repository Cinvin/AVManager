/*!
 * MediaElement.js
 * http://www.mediaelementjs.com/
 *
 * Wrapper that mimics native HTML5 MediaElement (audio and video)
 * using a variety of technologies (pure JavaScript, Flash, iframe)
 *
 * Copyright 2010-2017, John Dyer (http://j.hn/)
 * License: MIT
 *
 */
!function n(l, o, s) { function d(t, e) { if (!o[t]) { if (!l[t]) { var i = "function" == typeof require && require; if (!e && i) return i(t, !0); if (c) return c(t, !0); var a = new Error("Cannot find module '" + t + "'"); throw a.code = "MODULE_NOT_FOUND", a } var r = o[t] = { exports: {} }; l[t][0].call(r.exports, function (e) { return d(l[t][1][e] || e) }, r, r.exports, n, l, o, s) } return o[t].exports } for (var c = "function" == typeof require && require, e = 0; e < s.length; e++)d(s[e]); return d }({ 1: [function (e, t, i) { "use strict"; Object.assign(mejs.MepDefaults, { airPlayText: null }), Object.assign(MediaElementPlayer.prototype, { buildairplay: function () { if (window.WebKitPlaybackTargetAvailabilityEvent) { var r = this, e = mejs.Utils.isString(r.options.airPlayText) ? r.options.airPlayText : "AirPlay", n = document.createElement("div"); n.className = r.options.classPrefix + "button " + r.options.classPrefix + "airplay-button", n.innerHTML = '<button type="button" aria-controls="' + r.id + '" title="' + e + '" aria-label="' + e + '" tabindex="0"></button>', n.addEventListener("click", function () { r.media.originalNode.webkitShowPlaybackTargetPicker() }); var t = r.media.originalNode.getAttribute("x-webkit-airplay"); t && "allow" === t || r.media.originalNode.setAttribute("x-webkit-airplay", "allow"), r.media.originalNode.addEventListener("webkitcurrentplaybacktargetiswirelesschanged", function () { var e = r.media.originalNode.webkitCurrentPlaybackTargetIsWireless ? "Started" : "Stopped", t = r.media.originalNode.webkitCurrentPlaybackTargetIsWireless ? "active" : "", i = n.querySelector("button"), a = mejs.Utils.createEvent("airplay" + e, r.media); r.media.dispatchEvent(a), "active" === t ? mejs.Utils.addClass(i, "active") : mejs.Utils.removeClass(i, "active") }), r.media.originalNode.addEventListener("webkitplaybacktargetavailabilitychanged", function (e) { "available" === e.availability && r.addControlElement(n, "airplay") }) } } }) }, {}] }, {}, [1]);


