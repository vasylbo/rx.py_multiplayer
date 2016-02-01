PIXI = require("pixi.js")
Bacon = require("baconjs")

createView = (newOnes, updates, enterFrame, user, c) ->
  view = new PIXI.Container()

  back = createBack(c.MAP_WIDTH, c.MAP_WIDTH)
  view.addChild(back)

  newOnes.onValue((p) -> addPlayer(view, p))

  playerUpdate = updates.flatMap((d) ->
    Bacon.fromArray(d)
  ).map(({id, t, data}) ->
    v = view.getChildByName(id)
    {id, t, data, v}
  )

  movers = playerUpdate
    .filter(({t}) -> t == "d")
    .groupBy(idKey, dataLimitGroup)
    .flatMap((dirChanges) ->
      stopper = dirChanges
        .mapEnd(-> null)
        .filter((val) -> val == null)
        .take(1)

      dirChanges
        .toProperty()
        .sampledBy(enterFrame, (m, e) -> [m, e])
        .takeUntil(stopper)
    )

  movers
    .onValue(([{v, data}, dt]) ->
      speed = c.SPEED * dt
      v.mx += data.x * speed
      v.my += data.y * speed
      v.x = Math.ceil(v.mx)
      v.y = Math.ceil(v.my)
    )

  positionUpdates = playerUpdate
    .filter(({t}) -> t == "pos")
  positionUpdates.onValue(updatePosition)

  user.sampledBy(enterFrame, (u, e) ->
    {id: u.hero.id, view, c}
  ).onValue(onEnterFrame)

  view

addPlayer = (container, player) =>
  view = new PIXI.Container()
  view.name = player.id

  gfx = new PIXI.Graphics()
  gfx.name = "graphics"
  gfx.beginFill(0x00ff00)
  gfx.drawCircle(0, 0, player.size)
  gfx.endFill()
  view.addChild(gfx)

  name = new PIXI.Text(player.name)
  view.addChild(name)

  view.mx = view.x = player.pos.x
  view.my = view.y = player.pos.y

  container.addChild(view)
  container

# center view on player
onEnterFrame = ({id, view, c}) ->
  hero = view.getChildByName(id)
  nX = c.APP_WIDTH / 2 - hero.x
  nY = c.APP_HEIGHT / 2 - hero.y
  view.x = Math.ceil(lerp(view.x, nX, 0.2))
  view.y = Math.ceil(lerp(view.y, nY, 0.2))


updatePosition = ({v, data}) ->
  v.mx = data.x
  v.my = data.y
  v.x = Math.ceil(v.mx)
  v.y = Math.ceil(v.my)

createBack = (w, h) ->
  g = new PIXI.Graphics()
  g.beginFill(0xbbbbbb)
  g.drawRect(0, 0, 21, 21)
  g.lineStyle(1, 0x000000)
  g.moveTo(0, 11)
  g.lineTo(21, 11)
  g.moveTo(11, 0)
  g.lineTo(11, 21)
  g.endFill()
  texture = g.generateTexture()
  new PIXI.TilingSprite(texture, w, h)

idKey = (val) ->
  val.id

dataLimitGroup = (groupedStream, groupStartEvent) ->
  dirs = groupedStream.filter(({data}) -> data?)
  ends = groupedStream.filter(({data}) -> not data?).take(1)
  dirs.takeUntil(ends)

# linear interpolation
lerp = (a, b, t) ->
  a * (1 - t) + b * t

module.exports = createView