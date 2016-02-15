Bacon = require("baconjs")
createView = require("./viewEffects")

connectToServer = (c) ->
  ws = new WebSocket(c.url)
  messages = Bacon
    .fromEventTarget(ws, 'message', (m) -> JSON.parse(m.data))

  messages.ofType = (tp) ->
    @filter((m) -> m?.t == tp)
  messages.dataOfType = (tp) ->
    @ofType(tp).map(".data")

  {messages, ws}


logIn = ({messages, ws}) ->
  user = messages
    .take(1)
    .flatMap((value) ->
      {id, name, ts} = value
      Bacon.combineTemplate({id, name, ws}))

  pongs = messages
    .ofType("pong")

  timeDelta = pongs.map(
    ({ts, lts}) ->
      cts = new Date().getTime()
      Math.round(cts - ts)
  )

  timeDelta.log("Ping:")

  serverTime = timeDelta
    .sampledBy(Bacon.interval(16), (dt, i) ->
      cts = new Date().getTime()
      ts = Math.round(cts + dt)
      ts
    )

  Bacon.interval(1000).onValue(->
    m = {t:"ping", ts:new Date().getTime()}
    ws.send(JSON.stringify(m))
  )

  newPlayers = messages
    .dataOfType("new_player")
    .flatMap((players) ->
      Bacon.fromArray(players))

  removedPlayers = messages
    .dataOfType("removed_player")

  updates = messages
    .ofType("up")

  {user, newPlayers, removedPlayers, updates, serverTime}


startGame = (enterFrame, clicks, c) ->
  connection = connectToServer(c)
  {user, newPlayers, removedPlayers, updates, serverTime} =
    logIn(connection)

  userHero = user
    .sampledBy(newPlayers, (user, hero) -> {user, hero})
    .filter(({user, hero}) -> user.id == hero.id)
    .toProperty()

  view = createView(newPlayers, removedPlayers,
    updates, enterFrame, userHero, serverTime, c)

  clicks
    .onValue((m) ->
      m.t = "d"
      connection.ws.send(JSON.stringify(m))
    )

  {view}

module.exports = {startGame}