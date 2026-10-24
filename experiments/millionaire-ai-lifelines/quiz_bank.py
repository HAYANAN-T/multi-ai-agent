"""Original, manually authored multiple-choice display questions. The agent solver is synthetic, not an LLM.
Question text is for the reader; ground-truth correctness is used by the controlled environment only.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Question:
    prompt: str
    options: tuple[str, str, str, str]
    correct: int
    category: str

EASY = [
Question('Which planet is known as the Red Planet?',('Venus','Mars','Jupiter','Mercury'),1,'Space'),
Question('What is the chemical symbol for gold?',('Au','Ag','Fe','Pb'),0,'Science'),
Question('Which ocean is the largest on Earth?',('Indian','Pacific','Arctic','Atlantic'),1,'Geography'),
Question('Who painted the Mona Lisa?',('Monet','Da Vinci','Picasso','Van Gogh'),1,'Art'),
Question('How many sides does a hexagon have?',('Five','Seven','Six','Eight'),2,'Mathematics'),
Question('What gas do plants absorb during photosynthesis?',('Oxygen','Nitrogen','Hydrogen','Carbon dioxide'),3,'Science'),
Question('Which is the capital of Japan?',('Seoul','Kyoto','Tokyo','Osaka'),2,'Geography'),
Question('What organ pumps blood around the body?',('Liver','Brain','Heart','Lung'),2,'Biology'),
Question('Which instrument measures temperature?',('Barometer','Thermometer','Anemometer','Altimeter'),1,'Science'),
Question('Which continent contains Kenya?',('South America','Asia','Africa','Europe'),2,'Geography'),
Question('What is the smallest prime number?',('1','2','3','0'),1,'Mathematics'),
Question('What is H₂O commonly called?',('Ammonia','Salt','Water','Methane'),2,'Science'),
]
MEDIUM = [
Question('Which element has the chemical symbol W?',('Tungsten','Tin','Tantalum','Titanium'),0,'Science'),
Question('What is the deepest known ocean trench?',('Java Trench','Puerto Rico Trench','Mariana Trench','Tonga Trench'),2,'Geography'),
Question('Which scientist proposed continental drift in 1912?',('James Hutton','Alfred Wegener','Charles Lyell','Marie Tharp'),1,'Science'),
Question('Which planet has the shortest orbital period?',('Venus','Mars','Mercury','Earth'),2,'Space'),
Question('Which novel begins with "Call me Ishmael"?',('Moby-Dick','Jane Eyre','Dracula','The Odyssey'),0,'Literature'),
Question('Who formulated the laws of planetary motion?',('Johannes Kepler','Isaac Newton','Galileo Galilei','Edmond Halley'),0,'Science'),
Question('Which country is home to the ancient city of Petra?',('Egypt','Jordan','Greece','Turkey'),1,'History'),
Question('Which unit measures electric resistance?',('Watt','Volt','Ohm','Ampere'),2,'Physics'),
Question('Which language family includes Finnish?',('Indo-European','Uralic','Afro-Asiatic','Sino-Tibetan'),1,'Language'),
Question('Who wrote the novel "Things Fall Apart"?',('Chinua Achebe','Ngũgĩ wa Thiong’o','Wole Soyinka','Ben Okri'),0,'Literature'),
Question('Which astronomer identified the moons Io, Europa, Ganymede and Callisto?',('Tycho Brahe','Galileo Galilei','William Herschel','Edwin Hubble'),1,'Space'),
Question('What does DNA stand for?',('Dinucleic Acid','Deoxyribonucleic Acid','Dynamic Nuclear Acid','Dioxyribose Acid'),1,'Biology'),
]
HARD = [
Question('What is the SI unit of catalytic activity?',('Becquerel','Katal','Henry','Weber'),1,'Science'),
Question('Which mathematician first published the concept of a Turing machine?',('Alonzo Church','Kurt Gödel','Alan Turing','John von Neumann'),2,'Computing'),
Question('In which year was the first Nobel Prize in Physics awarded?',('1895','1901','1905','1911'),1,'History'),
Question('Which moon has the solar system’s densest atmosphere?',('Europa','Titan','Ganymede','Triton'),1,'Space'),
Question('The Chandrasekhar limit is mainly associated with which objects?',('White dwarfs','Neutron stars','Red giants','Black holes'),0,'Astrophysics'),
Question('Which mathematician proved the prime number theorem in 1896 alongside Hadamard?',('Émile Borel','Charles-Jean de la Vallée Poussin','Henri Poincaré','David Hilbert'),1,'Mathematics'),
Question('What is the atomic number of osmium?',('74','76','78','80'),1,'Chemistry'),
Question('Which composer completed the opera "Turandot" after Puccini’s death?',('Franco Alfano','Pietro Mascagni','Ottorino Respighi','Arrigo Boito'),0,'Music'),
Question('Which spacecraft first entered orbit around Saturn?',('Voyager 1','Cassini','Pioneer 11','New Horizons'),1,'Space'),
Question('Which physicist proposed the exclusion principle?',('Niels Bohr','Wolfgang Pauli','Max Planck','Erwin Schrödinger'),1,'Physics'),
Question('The ancient writing system Linear B primarily recorded which language?',('Etruscan','Mycenaean Greek','Latin','Phoenician'),1,'History'),
Question('Which mathematician is associated with the 1931 incompleteness theorems?',('Bertrand Russell','David Hilbert','Kurt Gödel','Emmy Noether'),2,'Mathematics'),
]
BANK = (EASY, MEDIUM, HARD)
