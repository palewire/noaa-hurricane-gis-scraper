export function Card({title, children} = {}) {
    return (
      <div className="card">
        {title ? <h2>{title}</h2> : null}
        {children}
      </div>
    );
}

export function CardList({cards} = {}) {
    console.log(cards);
    return (
    <div class="card-list">
      <div className="card-list">
        {cards.map((d) => (
          <Card title={d.id}>{d.datetime}</Card>
        ))}
      </div>
    </div>
    );
}
