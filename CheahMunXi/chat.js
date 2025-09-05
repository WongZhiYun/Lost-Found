fetch('/users')
  .then(res => res.json())
  .then(users => {
    const sidebar = document.querySelector('.sidebar');
    users.forEach(user => {
      const link = document.createElement('a');
      link.href = `chat.html?user=${user.username}`;
      link.className = 'user';
      link.innerHTML = `<img src="https://robohash.org/${user.username}?bgset=bg2"><span>${user.username}</span>`;
      sidebar.appendChild(link);
    });
  });
