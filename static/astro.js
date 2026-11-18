/* astro.js — fondo espacial reactivo para <html data-event="astro">
   - Estrellas con paralaje y lente gravitacional
   - Galaxia espiral girando al fondo y nebulosas
   - Agujero negro anclado en la esquina inferior derecha (reacciona a clics)
   - Clic = onda de choque + destello de luz
   - Las tarjetas se iluminan cuando el agujero negro pasa cerca
   - Botón ✨ para pausar/reanudar (se recuerda) */
(function () {
    'use strict';
    var html = document.documentElement;
    if (html.getAttribute('data-event') !== 'astro') {
        console.warn('astro.js: falta data-event="astro" en la etiqueta <html>');
        return;
    }
    console.info('astro.js: cargado');

    var TAU = Math.PI * 2;
    var DPR = Math.min(window.devicePixelRatio || 1, 1.5);
    var W = 0, H = 0;
    var paused = false;
    try { paused = localStorage.getItem('astroPaused') === '1'; } catch (e) {}

    function layer(z) {
        var c = document.createElement('canvas');
        c.setAttribute('aria-hidden', 'true');
        c.style.cssText = 'position:fixed;left:0;top:0;width:100%;height:100%;' +
                          'pointer-events:none;z-index:' + z;
        document.body.appendChild(c);
        return c;
    }
    var cs = layer(-1);   /* estrellas: detrás del contenido */
    var cf = layer(6);    /* agujero negro y luz: encima    */
    var gs = cs.getContext('2d');
    var gf = cf.getContext('2d');
    if (!gs || !gf) return;
    html.classList.add('astro-on');

    /* ── Estado ─────────────────────────────────────────────────────── */
    var hx = 0, hy = 0, mx = 0, my = 0, lastMove = -1e9;
    var tt = 0, flash = 0;
    var stars = [], disk = [], rings = [];
    var STAR_COLORS = ['255,255,255', '190,210,255', '255,226,170'];

    function resize() {
        W = window.innerWidth; H = window.innerHeight;
        [cs, cf].forEach(function (c) { c.width = W * DPR; c.height = H * DPR; });
        gs.setTransform(DPR, 0, 0, DPR, 0, 0);
        gf.setTransform(DPR, 0, 0, DPR, 0, 0);
        seedStars();
    }
    function seedStars() {
        stars = [];
        var n = Math.round(W * H / 5200);
        for (var i = 0; i < n; i++) {
            stars.push({
                x: Math.random() * W, y: Math.random() * H,
                z: .25 + Math.random() * .75,
                r: Math.random() * 1.2 + .35,
                p: Math.random() * TAU, s: .5 + Math.random() * 1.5,
                c: STAR_COLORS[(Math.random() * 3) | 0]
            });
        }
    }
    (function seedDisk() {
        for (var i = 0; i < 520; i++) {
            var n = 1.5 + Math.pow(Math.random(), 1.5) * 3.2;
            disk.push({
                a: Math.random() * TAU, n: n,
                w: .006 / Math.pow(n, 1.5),            /* rad/ms: más cerca, más rápido */
                b: .4 + Math.random() * .6,
                s: .8 + Math.random() * 1.6
            });
        }
    })();

    /* ── Galaxia espiral (se dibuja una vez y luego solo se gira) ───── */
    function gauss() { return (Math.random() + Math.random() + Math.random() - 1.5) / 1.5; }
    function buildGalaxy() {
        var S = 760, c = document.createElement('canvas');
        c.width = c.height = S;
        var g = c.getContext('2d'), cx = S / 2, R0 = S * .46, i;
        g.globalCompositeOperation = 'lighter';

        var halo = g.createRadialGradient(cx, cx, 0, cx, cx, R0);
        halo.addColorStop(0, 'rgba(255,220,170,.55)');
        halo.addColorStop(.18, 'rgba(255,190,140,.22)');
        halo.addColorStop(.5, 'rgba(110,90,230,.10)');
        halo.addColorStop(1, 'rgba(60,70,200,0)');
        g.fillStyle = halo; g.fillRect(0, 0, S, S);

        var ARMS = 3;
        for (i = 0; i < 9000; i++) {
            var t = Math.pow(Math.random(), .75);
            var r = t * R0;
            var ang = (i % ARMS) * (TAU / ARMS) + t * 6.2;
            var sc = gauss() * (.025 + .085 * t) * R0;
            var px = cx + Math.cos(ang) * r + Math.cos(ang + 1.5708) * sc;
            var py = cx + Math.sin(ang) * r + Math.sin(ang + 1.5708) * sc;
            var warm = 1 - t;
            var rr = (150 + 105 * warm) | 0, gg = (165 + 65 * warm) | 0, bb = (255 - 70 * warm) | 0;
            if (Math.random() < .035) { rr = 255; gg = 110; bb = 170; }   /* regiones rosadas */
            var a = (.10 + Math.random() * .4) * (1 - t * .55);
            var sz = .5 + Math.random() * 1.4 * (1 - t * .4);
            g.fillStyle = 'rgba(' + rr + ',' + gg + ',' + bb + ',' + a.toFixed(2) + ')';
            g.beginPath(); g.arc(px, py, sz, 0, TAU); g.fill();
        }
        var core = g.createRadialGradient(cx, cx, 0, cx, cx, R0 * .2);
        core.addColorStop(0, 'rgba(255,245,225,.95)');
        core.addColorStop(.4, 'rgba(255,205,150,.45)');
        core.addColorStop(1, 'rgba(255,170,110,0)');
        g.fillStyle = core; g.fillRect(0, 0, S, S);
        return c;
    }
    var galaxy = buildGalaxy();

    resize();
    hx = W - holeR() * 2.9; hy = H - holeR() * 2.7;
    mx = W / 2; my = H / 2;

    /* ── Reactividad ────────────────────────────────────────────────── */
    window.addEventListener('pointermove', function (e) {
        mx = e.clientX; my = e.clientY; lastMove = performance.now();
        var c = e.target && e.target.closest ? e.target.closest('.erp-card, .erp-module-card') : null;
        if (c) {
            var r = c.getBoundingClientRect();
            c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
            c.style.setProperty('--my', (e.clientY - r.top) + 'px');
        }
    }, { passive: true });

    window.addEventListener('pointerdown', function (e) {
        if (paused) return;
        mx = e.clientX; my = e.clientY; lastMove = performance.now();
        rings.push({ x: e.clientX, y: e.clientY, r: 6, a: .7 });
        rings.push({ x: hx, y: hy, r: 10, a: .5 });
        flash = Math.min(1.5, flash + .8);
    }, { passive: true });

    window.addEventListener('scroll', function () {
        if (!paused) flash = Math.min(1.5, flash + .06);
    }, { passive: true });

    var rt;
    window.addEventListener('resize', function () {
        clearTimeout(rt); rt = setTimeout(resize, 120);
    });

    /* ── Botón pausar/reanudar ──────────────────────────────────────── */
    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'astro-toggle';
    function paintBtn() {
        btn.textContent = paused ? '▶' : '✨';
        btn.title = paused ? 'Reanudar animación espacial' : 'Pausar animación espacial';
        btn.setAttribute('aria-label', btn.title);
    }
    btn.addEventListener('click', function () {
        paused = !paused;
        try { localStorage.setItem('astroPaused', paused ? '1' : '0'); } catch (e) {}
        paintBtn();
    });
    paintBtn();
    document.body.appendChild(btn);
    if (paused) console.info('astro.js: en PAUSA, pulsa el botón ▶ para reanudar');

    /* ── Física ─────────────────────────────────────────────────────── */
    function holeR() {
        var base = Math.max(36, Math.min(70, Math.min(W, H) * .075));
        return base * (1 + .04 * Math.sin(tt * .003)) * (1 + .25 * flash);
    }

    function update(dt, now) {
        if (paused) return;
        tt += dt;
        var R = holeR();
        /* anclado a la esquina inferior derecha, con vaivén suave y leve paralaje */
        var gx = W - R * 2.9 + Math.sin(tt * .0004) * 7 - (mx - W / 2) * .012;
        var gy = H - R * 2.7 + Math.cos(tt * .00055) * 6 - (my - H / 2) * .012;
        var k = 1 - Math.pow(1 - .06, dt / 16);
        hx += (gx - hx) * k; hy += (gy - hy) * k;
        for (var i = 0; i < disk.length; i++) disk[i].a += disk[i].w * dt;
        flash = Math.max(0, flash - dt * .0011);
        for (var j = rings.length - 1; j >= 0; j--) {
            var r = rings[j];
            r.r += dt * .55; r.a -= dt * .0006;
            if (r.a <= 0) rings.splice(j, 1);
        }
    }

    /* ── Dibujo: estrellas con lente gravitacional ──────────────────── */
    function drawBackdrop(dark) {
        var big = Math.max(W, H), i;
        gs.save();
        if (dark) {
            gs.globalCompositeOperation = 'lighter';
            var neb = [
                [.14, .22, .55, '90,60,200', .13],
                [.82, .30, .50, '40,120,210', .10],
                [.55, .85, .60, '200,60,150', .08]
            ];
            for (i = 0; i < neb.length; i++) {
                var n = neb[i];
                var nx = W * n[0] + Math.sin(tt * .00011 + i * 2) * 30;
                var ny = H * n[1] + Math.cos(tt * .00009 + i) * 24;
                var ng = gs.createRadialGradient(nx, ny, 0, nx, ny, big * n[2]);
                ng.addColorStop(0, 'rgba(' + n[3] + ',' + n[4] + ')');
                ng.addColorStop(1, 'rgba(' + n[3] + ',0)');
                gs.fillStyle = ng; gs.fillRect(0, 0, W, H);
            }
        }
        /* galaxia espiral inclinada que gira muy despacio */
        var size = Math.min(W, H) * 1.35;
        var gx = W * .28 - (mx - W / 2) * .01;
        var gy = H * .9 - (window.scrollY || 0) * .03;
        gs.globalCompositeOperation = dark ? 'lighter' : 'source-over';
        gs.globalAlpha = dark ? .85 : .22;
        gs.translate(gx, gy);
        gs.rotate(-.45); gs.scale(1, .5); gs.rotate(tt * .000018);
        gs.drawImage(galaxy, -size / 2, -size / 2, size, size);
        gs.restore();
    }

    function drawStars(R, dark) {
        gs.clearRect(0, 0, W, H);
        drawBackdrop(dark);
        var ox = mx - W / 2, oy = my - H / 2, sy = window.scrollY || 0;
        for (var i = 0; i < stars.length; i++) {
            var s = stars[i];
            var x = s.x - ox * s.z * .025;
            var y = ((s.y - sy * s.z * .08 - oy * s.z * .025) % H + H) % H;
            var dx = x - hx, dy = y - hy;
            var d = Math.sqrt(dx * dx + dy * dy) + .001;
            var boost = 1;
            if (d < R * 8) {
                if (d < R * 1.05) continue;                     /* tragada */
                var push = Math.min(R * 2.2, (R * R * 2.4) / d); /* desvío de la luz */
                x += dx / d * push; y += dy / d * push;
                boost = 1 + (1 - d / (R * 8)) * 1.8;
            }
            var tw = .4 + .6 * (.5 + .5 * Math.sin(tt * .002 * s.s + s.p));
            var a = Math.min(1, tw * boost * s.z + .08);
            gs.fillStyle = dark ? 'rgba(' + s.c + ',' + a.toFixed(2) + ')'
                                : 'rgba(40,50,130,' + (a * .7).toFixed(2) + ')';
            gs.beginPath(); gs.arc(x, y, s.r * (.85 + .15 * boost), 0, TAU); gs.fill();
        }
    }

    /* ── Dibujo: agujero negro + luz resplandeciente ────────────────── */
    function drawFx(R, dark) {
        var g = gf, add = dark ? 'lighter' : 'source-over';
        var A = dark ? 1 : .6, F = 1 + flash;
        var rot = -.2 + (hx / W - .5) * .18;
        var K = .13 + .02 * Math.sin(tt * .0006);
        var pulse = .5 + .5 * Math.sin(tt * .0024);
        var i, gr;

        g.clearRect(0, 0, W, H);
        g.globalCompositeOperation = add;

        /* resplandor general (bloom) */
        var br = R * (6 + 1.5 * pulse + 3 * flash);
        gr = g.createRadialGradient(hx, hy, R * .8, hx, hy, br);
        gr.addColorStop(0, 'rgba(255,170,70,' + (.38 * A * F).toFixed(3) + ')');
        gr.addColorStop(.35, 'rgba(255,120,30,' + (.14 * A).toFixed(3) + ')');
        gr.addColorStop(1, 'rgba(255,100,20,0)');
        g.fillStyle = gr; g.beginPath(); g.arc(hx, hy, br, 0, TAU); g.fill();

        /* rayos de luz giratorios */
        g.save(); g.translate(hx, hy);
        for (i = 0; i < 14; i++) {
            var ang = i * TAU / 14 + tt * .00007;
            var len = R * (7 + 3 * Math.sin(tt * .0013 + i * 1.7)) * F;
            g.save(); g.rotate(ang);
            var lg = g.createLinearGradient(R * 1.2, 0, len, 0);
            lg.addColorStop(0, 'rgba(255,200,120,' + (.1 * A * (1 + flash * 2)).toFixed(3) + ')');
            lg.addColorStop(1, 'rgba(255,150,60,0)');
            g.fillStyle = lg; g.beginPath();
            g.moveTo(R * 1.2, -R * .03); g.lineTo(len, -R * .22);
            g.lineTo(len, R * .22); g.lineTo(R * 1.2, R * .03);
            g.closePath(); g.fill(); g.restore();
        }
        g.restore();

        /* todo lo que sigue va inclinado con el disco */
        g.save(); g.translate(hx, hy); g.rotate(rot);

        /* chorros polares */
        for (var j = -1; j <= 1; j += 2) {
            var jl = R * (8 + 2 * Math.sin(tt * .004 + j)) * F;
            var jg = g.createLinearGradient(0, j * R, 0, j * jl);
            jg.addColorStop(0, 'rgba(255,225,170,' + (.5 * A * F).toFixed(3) + ')');
            jg.addColorStop(1, 'rgba(255,140,50,0)');
            g.fillStyle = jg; g.beginPath();
            g.moveTo(-R * .16, j * R); g.lineTo(R * .16, j * R);
            g.lineTo(R * .05, j * jl); g.lineTo(-R * .05, j * jl);
            g.closePath(); g.fill();
        }

        /* disco: gradiente con efecto Doppler (lado izquierdo más brillante) */
        var bg = g.createLinearGradient(-3.5 * R, 0, 3.5 * R, 0);
        bg.addColorStop(0, 'rgba(255,120,30,0)');
        bg.addColorStop(.18, 'rgba(255,150,60,' + (.9 * A).toFixed(3) + ')');
        bg.addColorStop(.38, 'rgba(255,245,220,' + A.toFixed(3) + ')');
        bg.addColorStop(.6, 'rgba(255,200,130,' + (.9 * A).toFixed(3) + ')');
        bg.addColorStop(.85, 'rgba(210,90,20,' + (.7 * A).toFixed(3) + ')');
        bg.addColorStop(1, 'rgba(180,60,10,0)');

        /* mitad trasera del disco */
        g.strokeStyle = bg; g.globalAlpha = .45; g.lineWidth = R * .16;
        g.beginPath(); g.ellipse(0, 0, 3.2 * R, 3.2 * R * K, 0, 0, TAU); g.stroke();
        g.globalAlpha = 1;

        /* imagen deformada del disco: arcos que envuelven la sombra */
        var ag = g.createLinearGradient(-1.6 * R, 0, 1.6 * R, 0);
        ag.addColorStop(0, 'rgba(255,255,235,' + (.95 * A).toFixed(3) + ')');
        ag.addColorStop(.35, 'rgba(255,190,100,' + (.9 * A).toFixed(3) + ')');
        ag.addColorStop(.7, 'rgba(230,110,30,' + (.8 * A).toFixed(3) + ')');
        ag.addColorStop(1, 'rgba(180,60,10,' + (.5 * A).toFixed(3) + ')');
        g.strokeStyle = ag; g.shadowColor = 'rgba(255,150,50,.85)'; g.shadowBlur = R * .35;
        g.lineWidth = R * .14;
        g.beginPath(); g.arc(0, 0, R * 1.16, Math.PI, TAU); g.stroke();
        g.globalAlpha = .55; g.lineWidth = R * .08;
        g.beginPath(); g.arc(0, 0, R * 1.1, 0, Math.PI); g.stroke();
        g.globalAlpha = 1; g.shadowBlur = 0;

        /* partículas traseras: chispas sobre el arco deformado */
        var p, c, s, bright, al, x, y, t, nl;
        for (i = 0; i < disk.length; i++) {
            p = disk[i]; s = Math.sin(p.a);
            if (s >= 0) continue;
            c = Math.cos(p.a);
            nl = 1.1 + (p.n - 1.5) * .1;
            x = c * nl * R; y = -Math.abs(s) * nl * R;
            bright = .45 + .55 * (.5 - .5 * c);
            g.fillStyle = 'rgba(255,220,160,' + (bright * p.b * .7 * A).toFixed(2) + ')';
            g.fillRect(x, y, p.s, p.s);
        }

        /* sombra del agujero negro (horizonte de sucesos) */
        g.globalCompositeOperation = 'source-over';
        g.fillStyle = '#000';
        g.beginPath(); g.arc(0, 0, R, 0, TAU); g.fill();
        g.globalCompositeOperation = add;

        /* anillo de fotones */
        g.strokeStyle = 'rgba(255,246,224,' + (.85 + .15 * pulse).toFixed(3) + ')';
        g.lineWidth = Math.max(2, R * .05);
        g.shadowColor = 'rgba(255,170,70,.95)'; g.shadowBlur = R * .5;
        g.beginPath(); g.arc(0, 0, R * 1.02, 0, TAU); g.stroke();

        /* mitad delantera del disco (cruza por delante de la sombra) */
        g.strokeStyle = bg; g.lineWidth = R * .2; g.shadowBlur = R * .4;
        g.beginPath(); g.ellipse(0, 0, 3.2 * R, 3.2 * R * K, 0, 0, Math.PI); g.stroke();
        g.strokeStyle = 'rgba(255,248,230,' + (.9 * A).toFixed(3) + ')';
        g.lineWidth = R * .05; g.shadowBlur = R * .25;
        g.beginPath(); g.ellipse(0, 0, 3.2 * R, 3.2 * R * K, 0, 0, Math.PI); g.stroke();
        g.shadowBlur = 0;

        /* partículas delanteras: gas orbitando con efecto Doppler */
        for (i = 0; i < disk.length; i++) {
            p = disk[i]; s = Math.sin(p.a);
            if (s < 0) continue;
            c = Math.cos(p.a);
            x = p.n * R * c; y = p.n * R * s * K;
            t = (p.n - 1.5) / 3.2;
            bright = .35 + .65 * (.5 - .5 * c);
            al = bright * p.b * (1 - t * .6) * A;
            g.fillStyle = 'rgba(255,' + ((235 - 145 * t) | 0) + ',' + ((190 - 170 * t) | 0) +
                          ',' + al.toFixed(2) + ')';
            g.fillRect(x, y, p.s, p.s);
        }
        g.restore();

        /* destello horizontal de lente */
        var fl = g.createLinearGradient(hx - R * 7, hy, hx + R * 7, hy);
        fl.addColorStop(0, 'rgba(255,210,140,0)');
        fl.addColorStop(.5, 'rgba(255,225,170,' + (.3 * A * F).toFixed(3) + ')');
        fl.addColorStop(1, 'rgba(255,210,140,0)');
        g.fillStyle = fl; g.fillRect(hx - R * 7, hy - 1.2, R * 14, 2.4);

        /* ondas de choque al hacer clic */
        g.lineWidth = 2;
        for (i = 0; i < rings.length; i++) {
            g.strokeStyle = 'rgba(255,205,130,' + (rings[i].a * A).toFixed(3) + ')';
            g.beginPath(); g.arc(rings[i].x, rings[i].y, rings[i].r, 0, TAU); g.stroke();
        }
        g.globalCompositeOperation = 'source-over';
    }

    /* ── Tarjetas iluminadas por la luz del agujero negro ───────────── */
    var lastLit = 0;
    function lightCards(R, now) {
        if (now - lastLit < 90) return;
        lastLit = now;
        var els = document.querySelectorAll('.erp-card, .erp-module-card');
        for (var i = 0; i < els.length; i++) {
            var r = els[i].getBoundingClientRect();
            var cx = Math.max(r.left, Math.min(hx, r.right));
            var cy = Math.max(r.top, Math.min(hy, r.bottom));
            var d = Math.sqrt((cx - hx) * (cx - hx) + (cy - hy) * (cy - hy));
            var v = Math.max(0, 1 - d / (R * 7));
            v = Math.min(1, v * v * (1 + flash));
            els[i].style.setProperty('--lit', v.toFixed(2));
        }
    }

    /* ── Bucle ──────────────────────────────────────────────────────── */
    var last = performance.now();
    function frame(now) {
        var dt = Math.max(0, Math.min(50, now - last)); last = now;
        try {
            update(dt, now);
            var R = holeR();
            var dark = html.getAttribute('data-theme') !== 'light';
            drawStars(R, dark);
            drawFx(R, dark);
            lightCards(R, now);
        } catch (err) {
            console.error('astro.js:', err);
        }
        requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
})();
