PIXI = require("pixi.js")
Bacon = require("baconjs")
{startGame} = require("./game")

c =
  APP_WIDTH: 800
  APP_HEIGHT: 600
  url: 'ws://localhost:8765'

initResize = (renderer) ->
  Bacon.fromEventTarget(window, 'resize')
    .toProperty({target:window})
    .map((event) ->
      t = event.target
      Math.min(
        t.innerWidth / c.APP_WIDTH,
        t.innerHeight / c.APP_HEIGHT)
    )
    .skipDuplicates()
    .onValue((ratio) ->
      width = c.APP_WIDTH * ratio
      height = c.APP_HEIGHT * ratio
      renderer.view.style.width = width + 'px'
      renderer.view.style.height = height + 'px'
    )

createEnterFrame = ->
  enterFrame = Bacon.fromBinder (sink) ->
    animate = ->
      sink()
      requestAnimationFrame(animate)
    requestAnimationFrame(animate)
  enterFrame

createClicksStream = (container, w, h) ->
  downs = Bacon.fromEventTarget(container, "mousedown")
    .merge(Bacon.fromEventTarget(container, "touchstart"))
  moves = Bacon.fromEventTarget(container, "mousemove")
    .merge(Bacon.fromEventTarget(container, "touchmove"))
  ends = Bacon.fromEventTarget(container, "mouseup")
    .merge(Bacon.fromEventTarget(container, "touchend"))

  hw = w / 2
  hh = h / 2
  downs.flatMap((e) ->
    Bacon.once(e)
      .merge(moves)
      .takeUntil(ends)
      .throttle(66)
      .map((m) ->
        cy = m.data.global.y
        cx = m.data.global.x
        x = cx - hw
        y = cy - hh
        l = Math.sqrt(x * x + y * y)
        {x: x / l, y: y / l})
      .mapEnd(null)
  )

createBackGround = (width, height) ->
  back = new PIXI.Graphics()
  back.beginFill(0xbbbbbb)
  back.drawRect(0, 0, width, height)
  back.endFill()
  back

init = ->
  stage = new PIXI.Container()
  stage.interactive = true
  renderer = new PIXI.autoDetectRenderer(
    c.APP_WIDTH, c.APP_HEIGHT)

  back = createBackGround(c.APP_WIDTH, c.APP_HEIGHT)
  stage.addChild(back)

  document.body.appendChild renderer.view
  initResize(renderer)

  enterFrame = createEnterFrame()
  enterFrame.onValue ->
    renderer.render(stage)

  clicks = createClicksStream(stage, c.APP_WIDTH, c.APP_HEIGHT)

  {view} = startGame(enterFrame, clicks, c)
  stage.addChild(view)

init()


