var client = new HttpClient();
var request = new HttpRequestMessage(HttpMethod.Get, "https://thispersondoesnotexist.com");
var response = await client.SendAsync(request);
response.EnsureSuccessStatusCode();
var imgStream = await response.Content.ReadAsStreamAsync();

 using var fileStream = new FileStream("FakeImage.jpg", FileMode.Create);
 await imgStream.CopyToAsync(fileStream);