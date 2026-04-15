export const options = [
  { value: "bananas", label: "Bananas" },
  { value: "oranges", label: "Oranges" },
  { value: "grapes", label: "Grapes" },
  { value: "strawberries", label: "Strawberries" },
  { value: "pears", label: "Pears" },
  { value: "peaches", label: "Peaches" },
  { value: "plums", label: "Plums" },
  { value: "cherries", label: "Cherries" },
  { value: "apricots", label: "Apricots" },
  { value: "lemons", label: "Lemons" },
  { value: "limes", label: "Limes" },
  { value: "tangerines", label: "Tangerines" },
  { value: "kiwis", label: "Kiwis" },
  { value: "mango", label: "Mango" },
  { value: "papaya", label: "Papaya" },
  { value: "pineapple", label: "Pineapple" },
  { value: "avocado", label: "Avocado" },
  { value: "cucumbers", label: "Cucumbers" },
  { value: "tomatoes", label: "Tomatoes" },
  { value: "peppers", label: "Peppers" },
  { value: "onions", label: "Onions" },
  { value: "garlic", label: "Garlic" },
  { value: "carrots", label: "Carrots" },
  { value: "celery", label: "Celery" },
  { value: "radish", label: "Radish" },
  { value: "cabbage", label: "Cabbage" },
  { value: "lettuce", label: "Lettuce" },
  { value: "spinach", label: "Spinach" },
  { value: "broccoli", label: "Broccoli" },
  { value: "chocolate", label: "Chocolate" },
  { value: "strawberry", label: "Strawberry" },
  { value: "vanilla", label: "Vanilla" },
];

export const getOptions = (value: string) =>
  new Promise<{ value: string; label: string }[]>((resolve) => {
    setTimeout(() => {
      if (value) {
        resolve(options.filter((o) => o.value.includes(value)));
      } else {
        resolve(options.slice(0, 5));
      }
    }, 2000);
  });
